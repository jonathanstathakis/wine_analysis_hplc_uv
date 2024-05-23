"""
Deconvolution
"""

import numpy as np
from scipy import optimize
from scipy.optimize._minpack_py import _lightweight_memoizer, _wrap_func
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ff_spy,
)

from wine_analysis_hplc_uv.signal_processing.deconvolution.types import FloatArray
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    ParamTbl,
)

# global store for least squares result metadata
curve_fit_output = []


def deconvolution(
    x: FloatArray,
    y: FloatArray,
    max_nfev: int = 100,
    verbose_level: int = 2,
):
    """
    deconvolve a signal y with time x into a matrix of single peak signals
    """
    # TODO: calculate the input parameters

    # TODO: fit the signal

    p0 = np.asarray([0, 0, 0, 0])
    bounds = tuple([np.asarray([-1, -1, -1, -1]), np.asarray([1, 1, 1, 1])])

    _curve_fit(
        x=x,
        y=y,
        max_nfev=max_nfev,
        p0=p0,
        bounds=bounds,
        verbose_level=verbose_level,
    )

    # TODO return the output
    output = None
    return output


def _curve_fit(
    x: FloatArray,
    y: FloatArray,
    p0: FloatArray,
    bounds: tuple[FloatArray, FloatArray],
    max_nfev: int = 100,
    verbose_level: int = 2,
) -> tuple[dict[str, pl.DataFrame], bool]:
    """
    Curve fit with the given optimizer. Mimics scipy.opimtize.curve_fit
    """
    assert isinstance(max_nfev, int), "expect int"

    # mimics that of scipy.optimize.curve_fit
    in_func = _lightweight_memoizer(
        _wrap_func(ff_spy.fit_skewnorms, x, y, transform=None)
    )

    res = optimize.least_squares(
        fun=in_func,
        x0=p0,
        bounds=bounds,
        max_nfev=max_nfev,
        verbose=verbose_level,
    )

    # passing the success bool out with the dicts then popping it above will allow me to stop iterations once a successful fit is achieved.

    return res


def check_in_bounds(param_tbl: ParamTbl):
    """
    raise an error if any value in p0 is oob
    """

    param_tbl_ = param_tbl.pipe(compute_in_bounds)

    # compute whether p0 is within lb

    # compute whether p0 is within ub
    # filter for any which are not within one of the above
    # raise an error and print the filtering

    if not all(param_tbl_.get_column("in_bounds")):
        oob_rows = param_tbl_.filter(pl.col("in_bounds").eq(False))

        raise ValueError(f"oob rows detected:\n{oob_rows}")


def _compute_popt(
    param_tbl: ParamTbl,
    x: FloatArray,
    y: FloatArray,
) -> ParamTbl:
    """
    Wrapper around curve_fit, intended for piping. first check if the input p0 is within the bounds, then unpack the table and call `_curve_fit`, finally add the output to
    """
    # ensure the parameters are in bounds
    param_tbl.pipe(check_in_bounds)

    # calculate popt

    # unpack bounds
    bounds = tuple(
        np.asarray(x, np.float64) for x in param_tbl.select(["lb", "ub"]).get_columns()
    )

    # check bounds is only length 2
    if len(bounds) > 2:
        raise ValueError("expect bounds to be length 2")

    # unpack p0
    p0 = np.asarray(param_tbl.get_column("p0"), dtype=np.float64)

    # calculate popt
    out = _curve_fit(
        x=x,
        y=y,
        p0=p0,
        bounds=bounds,
    )

    curve_fit_output.append(out)

    # get popt as series for input into df
    popt = pl.Series(name="popt", values=out["x"])

    # add popt to params table
    df = param_tbl.with_columns(popt)

    return df


def compute_in_bounds(df: ParamTbl):
    """
    compute whether p0 is within the lb or ub tables, added as columns "in_lb","in_ub", and "oob"
    """

    df_ = df.with_columns(
        pl.col("lb").lt(pl.col("p0")).alias("in_lb"),
        pl.col("ub").gt(pl.col("p0")).alias("in_ub"),
    ).with_columns(
        pl.when(pl.col("in_lb").eq(False))
        .then(True)
        .when(pl.col("in_ub").eq(False))
        .then(False)
        .otherwise(True)
        .alias("in_bounds"),
    )

    return df_
