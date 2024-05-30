"""
Test the generation of the bounds table
"""

import pytest
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_bounds,
)


@pytest.fixture(scope="module")
def bounds(x: pl.Series, mock_peak_maximas: pl.Series) -> pl.DataFrame:
    """
    The bounds table
    """

    bounds = gen_bounds.compute_bounds(x=x, amp=mock_peak_maximas)

    return bounds


def test_bounds_is_pl_df_not_empty(
    bounds: pl.DataFrame,
) -> None:
    """
    test that the bounds table is a polars dataframe and not empty
    """

    # is a pl DataFrame
    assert isinstance(bounds, pl.DataFrame)

    # is not empty
    assert not bounds.is_empty()
