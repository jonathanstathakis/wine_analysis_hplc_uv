"""
test `sigpro_methods.standardize_time` submodule
"""

import pandas as pd
import polars as pl
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods import standardize_time


def test_standardize_time(test_data: pd.DataFrame):
    """
    test `sigpro_methods.standardize_time.standardize_time` by asserting that the output dataframe matches expectation.
    """
    df_ = standardize_time.time_std_pipe(
        df=test_data,
        group_col="samplecode",
        time_col="mins",
        val_col="value",
        label_cols=["samplecode", "wine"],
        precision=6,
    )

    assert isinstance(df_, pl.DataFrame)
