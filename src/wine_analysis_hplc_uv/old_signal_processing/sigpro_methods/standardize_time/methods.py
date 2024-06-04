"""
Contains time standardization methods.
"""

import pandas as pd
import polars as pl


def standardize_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Take a tidy format df of column levels ['samplecode','wine','vars'] and vars
    of ['mins','value'] with 'i' index and return a df of same format but 'mins'
    as global index of datatype `pd.TimeDelta`, rounded to millisecond and resampled
    to mean sampling frequency.

    Refer to
    'notebooks/time_axis_characterisation_and_normalization.ipynb' and
    'notebooks/downsampling_signals.ipynb'.

    It has been determined that the minimum level of precision that ensures that each
    time axis value is unique is a millisecond scale, thus after datatype conversion
    the mins columns are rounded to "L". Next the 0 element time offset is corrected so
    element zero = 0 mins. then the dataset is moved to a universal time index as
    these modifications should have made them all equal.

    Test by asserting the geometry changes as expected.
    """

    # store to test the transformation later

    df_ = (
        df.pipe(from_multiindex_col_to_long_df)
        .pipe(set_df_dtypes)
        .pipe(correct_float_error)
        .pipe(correct_zero_offset)
        .pipe(resample_to_mean_frequency)
    )

    # a rudimentary transformation test. As we are expecting the same number of rows
    # after the transformation, test that. We're also expecting the number of columns
    # to be halved as we move from intra-sample 'mins' columns to 1 mins index which
    # is replacing 'i'.

    return df_


def from_multiindex_col_to_long_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    take a column unstacked dataframe and convert it to a long dataframe. inverse of
    `stack_wine_df` (?)
    """

    df_ = df.stack(["samplecode", "wine"]).reset_index()

    return df_


def set_df_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    specify the dtypes of the df columns prior to the pipe
    """

    df_ = df.astype(
        {"i": int, "samplecode": str, "wine": str, "mins": float, "value": float}
    )

    return df_


def stack_wine_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    stack the wine df on 'samplecode' and 'wine'
    """
    try:
        df_ = df.stack(["samplecode", "wine"])

        if not isinstance(df_, pd.DataFrame):
            raise TypeError(f"expected pandas DataFrame but got {type(df_)}")
    except Exception as e:
        raise e
    return df_


def correct_float_error(df: pd.DataFrame) -> pd.DataFrame:
    """
    convert to timedelta and round to milliseconds to correct float error
    """

    new_mins = df["mins"].round(6)

    df_ = df.assign(mins=new_mins)

    return df_


def correct_zero_offset(df: pd.DataFrame) -> pd.DataFrame:
    """
    correct 0 offset
    """
    import polars as pl

    df_ = pl.from_pandas(df)
    df_ = df_.with_columns(
        pl.col("mins").sub(pl.col("mins").min()).over("samplecode").alias("mins_corr")
    )

    check_aggs = df_.groupby("samplecode").agg(
        pl.min("mins").alias("mins_min"),
        pl.max("mins").alias("mins_max"),
        pl.min("mins_corr").alias("mins_corr_min"),
        pl.max("mins_corr").alias("mins_corr_max"),
        pl.min("i").alias("i_min"),
        pl.max("i").alias("i_max"),
    )

    # test if transformation behaves as expected within the context - across each group

    # minimum mins_corr value should be zero
    if not check_aggs.select(pl.col("mins_corr_min").eq(0).all()).item():
        raise ValueError("expect all 'mins_corr_min' to equal 0")

    # mins_corr_max should be mins_max - mins_min
    if not check_aggs.select(
        pl.col("mins_max").sub("mins_min").eq(pl.col("mins_corr_max")).all()
    ).item():
        raise ValueError(
            "expect all 'mins_corr_max' to equal diff of 'mins_max' and 'mins_min'"
        )

    # i should be same across df and df_
    if not pl.from_pandas(df).select("i").equals(df_.select("i")):
        raise ValueError("expect group row indexes to be equal")

    df_ = df_.drop("mins").rename({"mins_corr": "mins"})
    return df_


def resample_to_mean_frequency(df: pl.DataFrame) -> pl.DataFrame:
    """
    resample to the mean frequency.
    """
    import numpy as np

    # first get the mean frequency by samplecode
    mean_freqs_by_samplecode = df.groupby("samplecode").agg(
        pl.col("mins").diff().mean()
    )

    # then get the mean frequency across the whole dataset
    mean_freq = mean_freqs_by_samplecode.select(pl.col("mins").mean()).item()

    # # upsampl to mean_freq
    df_ = df.pipe(lambda df: df.resample(f"{np.round(mean_freq,5)}s").interpolate())

    return df_
