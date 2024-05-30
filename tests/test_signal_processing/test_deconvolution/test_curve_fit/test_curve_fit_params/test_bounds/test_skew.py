"""
test skew bounds computation
"""

import numpy as np
import pytest
import polars as pl
import polars.testing as pl_t
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_bounds,
)


@pytest.fixture(scope="module")
def computed_bounds_skew(n_peaks_mock: int) -> pl.DataFrame:
    """
    the skewation bounds table as computed by the `gen_bounds` module
    """
    skew_bounds = gen_bounds._compute_skew(n_peaks=n_peaks_mock)

    return skew_bounds


@pytest.fixture(scope="module")
def expected_skew_lb(n_peaks_mock: int) -> pl.Series:
    """
    The expected skew lb calculated independent of the gen_bounds module
    """

    return pl.Series(name="lb", values=[-np.inf] * n_peaks_mock)


@pytest.fixture(scope="module")
def expected_skew_ub(n_peaks_mock: int) -> pl.Series:
    """
    The expected skew ub calculated independent of the gen_bounds module
    """

    return pl.Series(name="lb", values=[+np.inf] * n_peaks_mock)


@pytest.fixture(scope="module")
def skew_lb_values_as_series(computed_bounds_skew: pl.DataFrame) -> pl.Series:
    """
    skew lower bound values as a series
    """
    return computed_bounds_skew.get_column("lb")


@pytest.fixture(scope="module")
def skew_ub_values_as_series(computed_bounds_skew: pl.DataFrame) -> pl.Series:
    """
    skew upper bound values as a series
    """
    return computed_bounds_skew.get_column("ub")


def test_skew_lb_eq_expectation(
    skew_lb_values_as_series: pl.Series,
    expected_skew_lb: pl.Series,
) -> None:
    """
    test if the computed skew lower bounds match expectation.
    """
    pl_t.assert_series_equal(
        left=skew_lb_values_as_series, right=expected_skew_lb, check_names=False
    )


def test_skew_ub_eq_expectation(
    skew_ub_values_as_series: pl.Series, expected_skew_ub: pl.Series
) -> None:
    """
    test if the computed skew upper bounds match expectation
    """
    pl_t.assert_series_equal(
        left=skew_ub_values_as_series, right=expected_skew_ub, check_names=False
    )
