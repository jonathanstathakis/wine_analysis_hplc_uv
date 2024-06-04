import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    FloatArray,
    ParamTbl,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_curve_fit_params,
)

# global store for least squares result metadata
curve_fit_output = []


def compute_popt(
    x: FloatArray,
    y: FloatArray,
    peak_maximas: pl.Series,
    peak_locations: pl.Series,
    peak_widths: pl.Series,
) -> ParamTbl:
    """
    Wrapper around curve_fit, intended for piping. first check if the input p0 is within the bounds, then unpack the table and call `_curve_fit`, finally add the output to
    """

    if any(x < 0):
        raise ValueError("please provide x > 0")

    param_tbl = gen_curve_fit_params.compute_curve_fit_params(
        x=x,
        peak_maximas=peak_maximas,
        peak_locations=peak_locations,
        peak_widths=peak_widths,
    )

    # ensure p0 is within the bounds
    check_in_bounds(param_tbl=param_tbl)

    p0, bounds = gen_curve_fit_params.extract_params(param_tbl=param_tbl)

    # calculate popt
    out = _curve_fit(
        x=x,
        y=y,
        p0=p0,
        bounds=bounds,
    )

    curve_fit_output.append(out)

    # get popt as series for input into df
    popt = pl.Series(name="popt", values=out[0]["x"])

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


def _curve_fit():
    pass


def check_in_bounds(param_tbl: pl.DataFrame):
    pass
