"""
A module dedicated to the calculation of the curve fit input parameters - initial guess and
bounds
"""

import numpy as np
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_bounds,
    gen_p0,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution import types


def compute_curve_fit_params(
    x: pl.Series,
    peak_maximas: pl.Series,
    peak_locations: pl.Series,
    peak_widths: pl.Series,
) -> pl.DataFrame:
    """
    Compute the bounds and initial guess input of least squares
    """

    # get the p0 table
    p0 = gen_p0._compute_p0(
        peak_maximas=peak_maximas,
        peak_locations=peak_locations,
        peak_widths=peak_widths,
    )

    # get the bounds table
    bounds = gen_bounds.compute_bounds(x=x, amp=peak_maximas)

    # join the two
    param_tbl = p0.join(bounds, on=["peak", "param", "param_order"], how="left").sort(
        "peak", "param_order"
    )

    return param_tbl


def _extract_col_as_float_array(df: pl.DataFrame, col: str) -> types.FloatArray:
    """
    Extract `col` from `df` as a np float array
    """
    x = np.asarray(df.get_column("p0"), dtype=np.float64)
    return x


def _extract_p0(param_tbl: pl.DataFrame) -> types.FloatArray:
    """
    extract p0 from `param_tbl` as a np float array
    """
    x = _extract_col_as_float_array(df=param_tbl, col="p0")
    return x


def _extract_bounds(
    param_tbl: pl.DataFrame,
) -> tuple[types.FloatArray, types.FloatArray]:
    """
    extract bounds from `param_tbl` as a tuple of np float arrays
    """
    lb = _extract_col_as_float_array(df=param_tbl, col="lb")
    ub = _extract_col_as_float_array(df=param_tbl, col="ub")
    return lb, ub


def extract_params(
    param_tbl: pl.DataFrame,
) -> tuple[types.FloatArray, tuple[types.FloatArray, types.FloatArray]]:
    """
    extract p0 and bounds from the `param_tbl`. First sorts by 'peak' and 'param_order' to ensure the values are in the expected order.
    """

    param_tbl_sorted = param_tbl.sort("peak", "param_order")

    p0 = _extract_p0(param_tbl=param_tbl_sorted)
    bounds = _extract_bounds(param_tbl=param_tbl_sorted)

    return p0, bounds
