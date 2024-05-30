"""
test scale bounds computation
"""

import pytest
import polars as pl
import polars.testing as pl_t
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_bounds,
)


@pytest.fixture(scope="module")
def computed_bounds_scale(x: pl.Series, n_peaks_mock: int) -> pl.DataFrame:
    """
    the scale bounds table as computed by the `gen_bounds` module
    """
    scale_bounds = gen_bounds._compute_scale(x=x, n_peaks=n_peaks_mock)

    return scale_bounds


@pytest.fixture(scope="module")
def expected_scale_lb(x: pl.Series, n_peaks_mock: int) -> pl.Series:
    """
    The expected scale lb calculated independent of the gen_bounds module
    """
    dx = pl.Series(name="x", values=x).diff().mean()
    return pl.Series(name="lb", values=[dx] * n_peaks_mock)


@pytest.fixture(scope="module")
def expected_scale_ub(x: pl.Series, n_peaks_mock: int) -> pl.Series:
    """
    The expected scale ub calculated independent of the gen_bounds module
    """
    x_ = pl.Series(name="x", values=x)

    half_range = (x.max() - x.min()) / 2
    return pl.Series(name="lb", values=[half_range] * n_peaks_mock)


@pytest.fixture(scope="module")
def scale_lb_values_as_series(computed_bounds_scale: pl.DataFrame) -> pl.Series:
    """
    scale lower bound values as a series
    """
    return computed_bounds_scale.get_column("lb")


@pytest.fixture(scope="module")
def scale_ub_values_as_series(computed_bounds_scale: pl.DataFrame) -> pl.Series:
    """
    scale upper bound values as a series
    """
    return computed_bounds_scale.get_column("ub")


def test_scale_lb_eq_expectation(
    scale_lb_values_as_series: pl.Series,
    expected_scale_lb: pl.Series,
) -> None:
    """
    test if the computed scale lower bounds match expectation.
    """
    pl_t.assert_series_equal(
        left=scale_lb_values_as_series, right=expected_scale_lb, check_names=False
    )


def test_scale_ub_eq_expectation(
    scale_ub_values_as_series: pl.Series, expected_scale_ub: pl.Series
) -> None:
    """
    test if the computed scale upper bounds match expectation
    """
    pl_t.assert_series_equal(
        left=scale_ub_values_as_series, right=expected_scale_ub, check_names=False
    )
