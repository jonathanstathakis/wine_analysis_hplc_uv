"""
Contains time standardization methods.
"""

import pandas as pd
import polars as pl


def from_multiindex_col_to_long_df(df: pd.DataFrame) -> pl.DataFrame:
    """
    take a column unstacked dataframe and convert it to a long dataframe. inverse of
    `stack_wine_df` (?)
    """

    df_ = df.stack(["samplecode", "wine"]).reset_index()
    df_ = pl.from_pandas(df_)

    return df_


def set_df_dtypes(df: pl.DataFrame) -> pl.DataFrame:
    """
    specify the dtypes of the df columns prior to the pipe
    """

    df_ = df.select(
        pl.col("i").cast(int),
        pl.col("samplecode").cast(str),
        pl.col("wine").cast(str),
        pl.col("mins").cast(float),
        pl.col("value").cast(float),
    )

    return df_


def correct_float_error(
    df: pl.DataFrame, time_col: str, precision: int
) -> pl.DataFrame:
    """
    round `time_col` to `precision`
    """

    df_ = df.with_columns(pl.col(time_col).round(decimals=precision))

    return df_


def correct_zero_offset(df: pl.DataFrame) -> pl.DataFrame:
    """
    correct 0 offset
    """
    df_ = df.with_columns(
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
    if not df.select("i").equals(df_.select("i")):
        raise ValueError("expect group row indexes to be equal")

    df_ = df_.drop("mins").rename({"mins_corr": "mins"})

    return df_
