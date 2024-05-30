"""
Generate curve fit parameter bounds values

amplitude: 0.1 * amp < amp < 10 * amp
loc: min(x) < x < max(x)
scale: dx < scale < half the range of x
skew: - inf < x < +inf
"""

import numpy as np
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    generic,
)


def compute_bounds(x, amp) -> pl.DataFrame:
    """
    compute the bounds, lb and ub, returned as a wide table. compute the parameter bounds by parameter then vertically stack. Peak index comes from amp. For the scalar bounds - loc, scale, skew, calculate the value and broadcast across `peak_idx`
    """

    # amp series is expected to contain one value per peak
    n_peaks = len(amp)

    # compute each parameter's bounds
    amp_ = _compute_amp(amp=amp)
    loc_ = _compute_loc(x=x, n_peaks=n_peaks)
    scale_ = _compute_scale(x=x, n_peaks=n_peaks)
    skew_ = _compute_skew(n_peaks=n_peaks)

    # form the bounds table

    bounds = pl.concat([amp_, loc_, skew_, scale_], how="vertical").sort(
        "peak", "param_order"
    )

    return bounds


def _bound_vals_to_df(
    lb: pl.Series,
    ub: pl.Series,
    parameter: str,
) -> pl.DataFrame:
    """
    convert a set of input series to a table with peak indexing as per the series order.
    """
    # gen the bounds df with a row index corresponding to the peak order
    df = (
        pl.DataFrame({"lb": lb, "ub": ub})
        .with_row_index("peak")
        .select("peak", pl.lit(parameter).alias("param"), "lb", "ub")
    )

    # add a param order col for later stage ordering

    df_ = _add_param_order_col(df=df)

    return df_


def _add_param_order_col(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add `param_order` col, specific for the bounds tables
    """
    df_ = generic.add_param_order_col(df=df).select(
        "peak", "param", "param_order", "lb", "ub"
    )

    return df_


def _compute_amp(amp: pl.Series) -> pl.DataFrame:
    """
    compute the lb and ub of amplitude as 0.1 and 10 * the input amplitude, respectively. Return as a dataframe indexed by peak with a parameter label, and two columns 'lb' and 'ub
    """
    lb = amp * 0.1
    ub = amp * 10

    out = _bound_vals_to_df(lb=lb, ub=ub, parameter="amp")

    return out


def _compute_loc(x: pl.Series, n_peaks: int) -> pl.DataFrame:
    """
    compute the location bounds as a function of x, the series of sampling points.
    """

    lb = pl.Series(name="lb", values=[min(x)] * n_peaks)
    ub = pl.Series(name="ub", values=[max(x)] * n_peaks)

    out = _bound_vals_to_df(lb=lb, ub=ub, parameter="loc")
    return out


def _compute_scale(x: pl.Series, n_peaks: int) -> pl.DataFrame:
    """
    compute the scale bounds as dx and half the range
    """
    dx = pl.Series(name="x", values=x).diff().mean()
    half_range = (max(x) - min(x)) / 2

    lb = pl.Series(name="lb", values=[dx] * n_peaks)
    ub = pl.Series(name="lb", values=[half_range] * n_peaks)

    out = _bound_vals_to_df(lb=lb, ub=ub, parameter="scale")

    return out


def _compute_skew(n_peaks: int) -> pl.DataFrame:
    """
    compute the skew bounds as - and + infinity
    """
    lb = pl.Series(name="lb", values=[-np.inf] * n_peaks)
    ub = pl.Series(name="ub", values=[+np.inf] * n_peaks)

    out = _bound_vals_to_df(lb=lb, ub=ub, parameter="skew")
    return out
