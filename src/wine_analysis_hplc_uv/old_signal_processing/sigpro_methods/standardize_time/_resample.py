"""
resample a dataframe
"""

import polars as pl
import pandas as pd


def resample_to_mean_freq(
    df: pl.DataFrame,
    time_col: str,
    group_col: str | list[str],
    value_col: str,
    label_cols: list[str],
) -> pl.DataFrame:
    """
    resample an input dataframe on by 'time' col. A convenience function wrapping `resample_groups_to_target`. Use that if a frequency other than the sample mean is required.
    """

    if group_col not in label_cols:
        raise ValueError("expect group_col to be in label_cols as it is a label")

    # get the mean frequency
    mean_freq = compute_mean_freq(df=df, time_col=time_col, group_col=group_col)

    # resample to the target
    df_ = resample_groups_to_target(
        df=df,
        target_freq=mean_freq,
        time_col=time_col,
        value_col=value_col,
        group_col=group_col,
        label_cols=label_cols,
    )

    return df_


def resample_groups_to_target(
    df: pl.DataFrame,
    time_col: str,
    value_col: str,
    group_col: str | list[str],
    target_freq: float,
    label_cols: list[str],
) -> pl.DataFrame:
    """
    resample the input dataframe on `time_col` to the target frequency `target_freq` across groups `group_col`
    """

    # produce the iterator
    resampled_frames = {}
    for key, grp in df.partition_by(group_col, as_dict=True).items():
        resampled_frames[key] = resample_frame_to_target(
            df=grp,
            time_col=time_col,
            target_dx=target_freq,
            value_col=value_col,
            label_cols=label_cols,
        )

    # concatenate the resampled frames together
    df_ = pl.concat(resampled_frames.values())

    return df_


def resample_frame_to_target(
    df: pl.DataFrame,
    time_col: str,
    value_col: str,
    target_dx: float,
    label_cols: list[str],
) -> pl.DataFrame:
    """
    resample `df` on `time_col` to `target_freq`

    polars/duckdb does not have the same resampling capability as pandas, so atm am using pandas

    interpolation after upsampling doesnt handle string columns, so need to manually ffill. This may cause errors if the upsampled value should be something else, be warned.

    The target frequency input is rounded to a precision of 9 prior to resampling.
    """

    # resample and interpolate new NaN a mean
    resampled_df = resample_and_interpolate_by_mean(
        df=df,
        target_dx=target_dx,
        time_col=time_col,
        value_col=value_col,
    )

    labelled_df = add_back_excluded_columns(
        input_df=df, resampled_df=resampled_df, label_cols=label_cols
    )

    # convert datetime column back to float in minutes

    # FIXME: interpolation causes repeating 'idx' column and mins. Need to extrapolate mins from the timedelta col, recompute the index.
    return labelled_df


def dt_to_mins(df: pl.DataFrame, datetime_col: str):
    """
    convert the datetime col back to float minutes
    """
    nanoseconds_to_minutes_factor = 1 / 1000 / 1000 / 1000 / 60
    df_ = df.with_columns(
        pl.col(datetime_col)
        .dt.total_nanoseconds()
        .mul(nanoseconds_to_minutes_factor)
        .alias("mins")
    ).drop("mins_td")

    return df_


def add_back_excluded_columns(
    input_df: pl.DataFrame,
    resampled_df: pl.DataFrame,
    label_cols: list[str],
) -> pl.DataFrame:
    """
    resampling non-float data is context-specific, easier to exclude then manually add
    back in. get the first values from each of the label columns and add them as new
    columns to the transformed df. This is necessary as the number of rows change after
    resampling.
    """
    excluded_vals = input_df.select(pl.first(label_cols))

    df_ = resampled_df.join(excluded_vals, how="cross")

    return df_


def resample_and_interpolate_by_mean(
    df: pl.DataFrame,
    time_col: str,
    value_col: str,
    target_dx: float,
) -> pl.DataFrame:
    """
    Interpolation is messy, ergo should only resample the relevant columns. Thus need to specify which is which in the function signature.
    """
    # resample to the target dx
    rule = _calculate_rule(target_dx=target_dx)

    # get the mins col as a timedelta
    td_col = time_col + "_td"
    pandas_df = to_pandas_with_td_col(df=df, time_col=time_col, td_col=td_col)

    resampled_df = (
        pandas_df.set_index(td_col)[[value_col]]
        .resample(rule=rule)
        .mean()
        .reset_index()
        .pipe(pl.from_pandas)
    )

    # ratio between nanoseconds and minutes scale
    df_ = dt_to_mins(df=resampled_df, datetime_col=td_col)
    return df_


def to_pandas_with_td_col(df: pl.DataFrame, time_col: str, td_col: str):
    df_ = df.to_pandas()
    df_[td_col] = pd.to_timedelta(arg=df.get_column(time_col).to_numpy(), unit="min")

    return df_


def _calculate_rule(target_dx: float) -> str:
    """
    pandas resample API accepts a chrono string representing a time step. Generate that from `target_dx`, anticipating a minutes units input.
    """

    rule = f"{round(target_dx, 9)}min"

    return rule


def compute_mean_freq(
    df: pl.DataFrame, time_col: str, group_col: str | list[str]
) -> float:
    """
    calculate the mean frequency of `time_col` over `group_col`
    """

    mean_freq = df.select(pl.col(time_col).diff().mean().over(group_col)).mean().item()

    return mean_freq
