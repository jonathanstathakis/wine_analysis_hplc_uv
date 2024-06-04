"""
resample a dataframe
"""

import polars as pl
import pandas as pd


def resample_to_mean_freq(
    df: pl.DataFrame, time_col: str, group_col: str | list[str]
) -> pl.DataFrame:
    """
    resample an input dataframe on by 'time' col. A convenience function wrapping `resample_groups_to_target`. Use that if a frequency other than the sample mean is required.
    """

    # get the mean frequency
    mean_freq = compute_mean_freq(df=df, time_col=time_col, group_col=group_col)

    # resample to the target
    df_ = resample_groups_to_target(
        df=df, target_freq=mean_freq, time_col=time_col, group_col=group_col
    )

    return df_


def resample_groups_to_target(
    df: pl.DataFrame,
    time_col: str,
    group_col: str | list[str],
    target_freq: float,
) -> pl.DataFrame:
    """
    resample the input dataframe on `time_col` to the target frequency `target_freq` across groups `group_col`
    """

    # produce the iterator
    resampled_frames = {}
    for key, grp in df.partition_by(group_col, as_dict=True).items():
        resampled_frames[key] = resample_frame_to_target(
            df=grp, time_col=time_col, target_freq=target_freq
        )

    # concatenate the resampled frames together
    df_ = pl.concat(resampled_frames.values())

    return df_


def resample_frame_to_target(
    df: pl.DataFrame,
    time_col: str,
    target_freq: float,
) -> pl.DataFrame:
    """
    resample `df` on `time_col` to `target_freq`

    polars/duckdb does not have the same resampling capability as pandas, so atm am using pandas

    interpolation after upsampling doesnt handle string columns, so need to manually ffill. This may cause errors if the upsampled value should be something else, be warned.

    The target frequency input is rounded to a precision of 9 prior to resampling.
    """
    td_time_col = time_col + "_td"

    # get the mins col as a timedelta
    df_ = df.to_pandas()
    df_[td_time_col] = pd.to_timedelta(
        arg=df.get_column(time_col).to_numpy(), unit="min"
    )
    import polars.selectors as cs

    # resample to the target freq
    rule = f"{round(target_freq, 9)}min"
    df_ = (
        df_.set_index(td_time_col)
        .resample(rule=rule)
        .interpolate()
        .reset_index()
        .pipe(pl.from_pandas)
        .with_columns(cs.string().forward_fill())
    )

    # drop timedelta col
    df_ = df_.drop(td_time_col)
    return df_


def compute_mean_freq(
    df: pl.DataFrame, time_col: str, group_col: str | list[str]
) -> float:
    """
    calculate the mean frequency of `time_col` over `group_col`
    """

    mean_freq = df.select(pl.col(time_col).diff().mean().over(group_col)).mean().item()

    return mean_freq
