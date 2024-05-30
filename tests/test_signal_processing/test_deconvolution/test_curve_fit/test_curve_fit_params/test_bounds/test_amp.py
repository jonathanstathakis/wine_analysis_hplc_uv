"""
test amplitude bound computation
"""

import pytest
import polars as pl
import polars.testing as pl_t
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_bounds,
)


@pytest.fixture(scope="module")
def computed_bounds_amp(mock_peak_maximas: pl.Series) -> pl.DataFrame:
    amp_bounds = gen_bounds._compute_amp(amp=mock_peak_maximas)

    return amp_bounds


@pytest.fixture(scope="module")
def expected_amp_lb(mock_peak_maximas: pl.Series) -> pl.Series:
    """
    The expected amp lb calculated independent of the gen_bounds module: 0.1 * maxima
    """

    return mock_peak_maximas * 0.1


@pytest.fixture(scope="module")
def expected_amp_ub(mock_peak_maximas: pl.Series) -> pl.Series:
    """
    The expected amp lb calculated independent of the gen_bounds module: 10 * maxima
    """

    return mock_peak_maximas * 10


@pytest.fixture(scope="module")
def amp_lb_values_as_series(computed_bounds_amp: pl.DataFrame) -> pl.Series:
    """
    amp lower bound values as a series
    """
    return computed_bounds_amp.get_column("lb")


@pytest.fixture(scope="module")
def amp_ub_values_as_series(computed_bounds_amp: pl.DataFrame) -> pl.Series:
    """
    amp upper bound values as a series
    """
    return computed_bounds_amp.get_column("ub")


def test_amp_lb_eq_expectation(
    amp_lb_values_as_series: pl.Series,
    expected_amp_lb: pl.Series,
) -> None:
    """
    test if the computed ampitude lower bounds match expectation.
    """
    pl_t.assert_series_equal(
        left=amp_lb_values_as_series, right=expected_amp_lb, check_names=False
    )


def test_amp_ub_eq_expectation(
    amp_ub_values_as_series: pl.Series, expected_amp_ub: pl.Series
) -> None:
    """
    test if the computed amplitude upper bounds match expectation
    """
    pl_t.assert_series_equal(
        left=amp_ub_values_as_series, right=expected_amp_ub, check_names=False
    )
