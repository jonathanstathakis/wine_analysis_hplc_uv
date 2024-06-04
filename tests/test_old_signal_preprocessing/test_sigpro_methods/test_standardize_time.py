"""
test `sigpro_methods.standardize_time` submodule
"""

import pytest
import pandas as pd
import polars as pl
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods import standardize_time
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods.standardize_time import (
    _methods as std_time_methods,
)


@pytest.fixture(scope="module")
def test_data():
    # set up environment
    data = pd.read_parquet(definitions.RAW_PARQ_PATH)

    return data


def test_standardize_time(test_data: pd.DataFrame):
    """
    test `sigpro_methods.standardize_time.standardize_time` by asserting that the output dataframe matches expectation.
    """
    df_ = standardize_time.standardize_time(
        df=test_data, group_col="samplecode", time_col="mins", precision=6
    )

    assert isinstance(df_, pl.DataFrame)


@pytest.fixture(scope="module")
def test_data_l(test_data: pd.DataFrame) -> pl.DataFrame:
    """
    return the test data in long form, as a polars dataframe
    """

    df_ = (
        test_data.pipe(std_time_methods.from_multiindex_col_to_long_df)
        .pipe(std_time_methods.set_df_dtypes)
        .pipe(pl.from_pandas)
    )

    return df_


def test_resample(test_data_l: pl.DataFrame) -> None:
    """
    test resampling routine
    """
    df_ = standardize_time.resample_to_mean_freq(
        df=test_data_l,
        time_col="mins",
        group_col="samplecode",
    )

    # to test, get the mean freq of `test_data_l`, and compare it to the freq of each group in df_. Each group should have the same frequency as the mean after transformation

    # compute the mean dx over the samples before transformation
    mean_dx = (
        test_data_l.select(pl.col("mins").diff().mean().over("samplecode"))
        .mean()
        .item()
    )

    # calculate the mean dx by sample after transformation
    check_aggs = df_.groupby("samplecode").agg(
        pl.col("mins").diff().mean().alias("mean_dx_tform")
    )

    # assert that all the mean dx are equal to the `mean_freq`. Have to round to 5 sig fig because polars is rounding the `mean_freq` for some reason

    is_all_eq = (
        check_aggs.with_columns(pl.lit(mean_dx).alias("mean_dx"))
        .with_columns(pl.col("mean_dx_tform").round(5), pl.col("mean_dx").round(5))
        .select(pl.col("mean_dx_tform").eq(pl.col("mean_dx")).all())
        .item()
    )

    assert is_all_eq, "samplewise mean dx not equal to dataset mean dx!"
