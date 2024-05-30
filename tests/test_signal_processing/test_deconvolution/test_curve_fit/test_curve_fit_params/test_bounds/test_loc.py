"""
test location bounds computation
"""

import pytest
import polars as pl
import polars.testing as pl_t
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_bounds,
)


@pytest.fixture(scope="module")
def computed_bounds_loc(x: pl.Series, n_peaks_mock: int) -> pl.DataFrame:
    """
    the location bounds table as computed by the `gen_bounds` module
    """
    loc_bounds = gen_bounds._compute_loc(x=x, n_peaks=n_peaks_mock)

    return loc_bounds


@pytest.fixture(scope="module")
def expected_loc_lb(x: pl.Series, n_peaks_mock: int) -> pl.Series:
    """
    The expected loc lb calculated independent of the gen_bounds module
    """

    return pl.Series(name="lb", values=[min(x)] * n_peaks_mock)


@pytest.fixture(scope="module")
def expected_loc_ub(x: pl.Series, n_peaks_mock: int) -> pl.Series:
    """
    The expected loc ub calculated independent of the gen_bounds module
    """

    return pl.Series(name="lb", values=[max(x)] * n_peaks_mock)


@pytest.fixture(scope="module")
def loc_lb_values_as_series(computed_bounds_loc: pl.DataFrame) -> pl.Series:
    """
    loc lower bound values as a series
    """
    return computed_bounds_loc.get_column("lb")


@pytest.fixture(scope="module")
def loc_ub_values_as_series(computed_bounds_loc: pl.DataFrame) -> pl.Series:
    """
    loc upper bound values as a series
    """
    return computed_bounds_loc.get_column("ub")


def test_loc_lb_eq_expectation(
    loc_lb_values_as_series: pl.Series,
    expected_loc_lb: pl.Series,
) -> None:
    """
    test if the computed location lower bounds match expectation.
    """
    pl_t.assert_series_equal(
        left=loc_lb_values_as_series, right=expected_loc_lb, check_names=False
    )


def test_loc_ub_eq_expectation(
    loc_ub_values_as_series: pl.Series, expected_loc_ub: pl.Series
) -> None:
    """
    test if the computed locatiion upper bounds match expectation
    """
    pl_t.assert_series_equal(
        left=loc_ub_values_as_series, right=expected_loc_ub, check_names=False
    )
