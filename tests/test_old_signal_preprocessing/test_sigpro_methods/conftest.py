import pytest
import pandas as pd
import polars as pl
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods.standardize_time import (
    _methods as std_time_methods,
)


@pytest.fixture(scope="module")
def test_data():
    # set up environment
    data = pd.read_parquet(definitions.RAW_PARQ_PATH)

    return data


@pytest.fixture(scope="module")
def test_data_l(test_data: pd.DataFrame) -> pl.DataFrame:
    """
    return the test data in long form, as a polars dataframe
    """

    df_ = std_time_methods.from_multiindex_col_to_long_df(df=test_data)
    df_ = std_time_methods.set_df_dtypes(df=df_)

    return df_
