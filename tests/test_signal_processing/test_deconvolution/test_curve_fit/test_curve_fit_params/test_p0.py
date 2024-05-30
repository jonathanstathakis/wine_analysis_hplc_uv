"""
testing module dedicated to the functions computing the p0 for curve fitting

TODO: move each parameter test to own module to reduce namespace bloat, match bounds test format
"""

import polars as pl
import polars.testing as pl_t
import numpy as np
import random
from numpy import typing as npt

# set the rng state for repeatability
random.seed(5)
type FloatArray = npt.NDArray[np.float64]


def test_compute_p0_is_df(
    p0: pl.DataFrame,
):
    """
    test computation of p0 by providing an input and comparing it to a mock output/
    """

    assert isinstance(p0, pl.DataFrame)


def test_p0_param_grps_correct_length(
    p0: pl.DataFrame,
    n_peaks_mock: int,
):
    # assert each param group is the same length as the input data
    param_len_df = (
        p0.groupby("param")
        .len()
        .with_columns(pl.lit(n_peaks_mock).alias("exp_len"))
        .with_columns(
            pl.col("len").eq(pl.col("exp_len")).alias("len_matches")
            )
    )  # fmt: skip

    assert param_len_df.select(
        pl.col("len_matches").all()
    ).item(), "expect each param group to have length equal to n_peaks!"

    # assert that the scales are half the input widths


def test_p0_scale_half_the_widths(
    p0: pl.DataFrame,
    mock_peak_widths: pl.Series,
):
    """
    expect the p0 scales to be half the input widths
    """

    # get the calculated scales (half widths)
    left = p0.filter(pl.col("param").eq("scale")).get_column("p0")

    # calculate half the widths indepdently
    right = mock_peak_widths * 0.5

    # check if all values are the same. Implies that the order is correct, as well as the calculations
    pl_t.assert_series_equal(left=left, right=right, check_names=False)


def test_p0_loc_eq_input(p0: pl.DataFrame, mock_peak_locs: pl.Series):
    """
    test that the input locs equal the locs present in p0
    """

    left = p0.filter(pl.col("param").eq("loc")).get_column("p0")
    right = mock_peak_locs

    pl_t.assert_series_equal(left=left, right=right, check_names=False)


def test_p0_skews(p0: pl.DataFrame, mock_skews: pl.Series):
    """
    test whether the p0 skews equal the mock skews.
    """

    left = p0.filter(pl.col("param").eq("skew")).get_column("p0")
    right = mock_skews

    pl_t.assert_series_equal(left=left, right=right, check_names=False)
