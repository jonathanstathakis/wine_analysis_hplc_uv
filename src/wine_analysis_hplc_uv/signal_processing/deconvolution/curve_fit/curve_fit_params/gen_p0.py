"""
generate curve fit parameter initial guess values
"""

from typing import Literal

import numpy as np
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    generic,
)


def _compute_p0(
    peak_maximas: pl.Series, peak_locations: pl.Series, peak_widths: pl.Series
) -> pl.DataFrame:
    for x in [peak_maximas, peak_locations, peak_widths]:
        if not isinstance(x, pl.Series):
            raise TypeError("expect pl Series!")
        if x.is_empty():
            raise ValueError("expect values!")

    amps = _compute_p0_amp(peak_maximas=peak_maximas)
    locs = _compute_p0_loc(peak_locations=peak_locations)
    scales = _compute_p0_scale(peak_widths=peak_widths)
    skews = _compute_p0_skew(n_peaks=len(peak_maximas))

    p0 = _form_p0(amps=amps, locs=locs, scales=scales, skews=skews)

    return p0


def _form_long_param_tbl(
    param_vals: pl.Series,
    param_label: Literal["amp", "loc", "scale", "skew"],
    idx_name: str = "peak",
) -> pl.DataFrame:
    """
    Standardized conversion of a polars Series containing the peak measurements to a
    long-form dataframe ready for stacking.
    """

    # input val
    parameter_vals = pl.Series(name=param_label, values=param_vals)

    # from series to long table, three cols: 'peak' idx, 'param' label, 'values'
    param_tbl = (
        pl.DataFrame(parameter_vals)
        .with_row_index(idx_name)
        .select(
            pl.col(idx_name),
            pl.lit(param_label).alias("param"),
            pl.col(param_label).alias("p0"),
        )
    )

    param_tbl_ = generic.add_param_order_col(df=param_tbl).select(
        "peak", "param", "param_order", "p0"
    )

    return param_tbl_


def _compute_p0_amp(peak_maximas: pl.Series) -> pl.DataFrame:
    """
    assemble the peak p0 amplitudes labelled by peak and parameter.
    """

    return _form_long_param_tbl(peak_maximas, "amp")


def _compute_p0_loc(peak_locations: pl.Series) -> pl.DataFrame:
    """
    calculate the initial guess of the locations as the measured peak maxima locations
    of the convoluted signal
    """

    return _form_long_param_tbl(peak_locations, "loc")


def _compute_p0_scale(peak_widths: pl.Series) -> pl.DataFrame:
    """
    compute the scale initial guess as half the peak width measured at half-height.
    """

    # as defined by cremerlab
    peak_widths_ = peak_widths * 0.5

    return _form_long_param_tbl(param_vals=peak_widths_, param_label="scale")


def _compute_p0_skew(n_peaks: int) -> pl.DataFrame:
    """
    the initial guess for skew is defined as zero, which assumes a normal distribution.
    Require the number of peaks to generate the table
    """

    skews = pl.Series(np.zeros(n_peaks))

    return _form_long_param_tbl(skews, param_label="skew")


def _form_p0(
    amps: pl.DataFrame, locs: pl.DataFrame, scales: pl.DataFrame, skews: pl.DataFrame
) -> pl.DataFrame:
    """
    Assemble the p0 from dfs for each parameter, vertically stacked then sorted by peak (time) order and parameter
    """

    p0 = pl.concat([amps, locs, scales, skews], how="vertical").sort(["peak", "param"])

    return p0
