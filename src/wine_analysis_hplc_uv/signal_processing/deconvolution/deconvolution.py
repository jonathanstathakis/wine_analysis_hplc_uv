"""
Deconvolution
"""

import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ff_spy,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    FloatArray,
    ParamTbl,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_curve_fit_params,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit import curve_fit


def deconvolution(
    x: FloatArray | pl.Series,
    y: FloatArray | pl.Series,
    max_nfev: int = 100,
    verbose_level: int = 2,
):
    """
    deconvolve a signal y with time x into a matrix of single peak signals
    """

    # validate the input

    x = pl.Series(name="x", values=x)
    y = pl.Series(name="y", values=y)

    # TODO: map the peaks
    peak_maximas = None
    peak_locations = None
    peak_widths = None

    # calculate the input parameters
    param_tbl = gen_curve_fit_params.compute_curve_fit_params(
        x=x,
        peak_maximas=peak_maximas,
        peak_locations=peak_locations,
        peak_widths=peak_widths,
    )
    p0, bounds = gen_curve_fit_params.extract_params(param_tbl=param_tbl)

    # TODO: fit the signal
    curve_fit.compute_popt(
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


def generate_pdfs(
    params: ParamTbl,
    x: FloatArray,
):
    """
    Calculate the pdf(s) from input distribution parameters: `params` and a sampling point array: `x`.
    """

    # iterate over the peak groups in `params`, generating a pdf for each peak
    def gen_pdfs(df: pl.DataFrame, x: FloatArray):
        param_dict = dict(df.select("param", "popt").iter_rows())

        peak_idx = df.select(pl.col("peak").first()).item()
        # compute the pdf
        return pl.DataFrame({"pdf": ff_spy.compute_skewnorm(x=x, **param_dict)}).select(
            pl.lit(peak_idx).alias("peak"), "pdf"
        )

    pdfs = params.groupby("peak", maintain_order=True).apply(
        lambda df: gen_pdfs(df=df, x=x)
    )
    return pdfs


def convolute_pdfs(pdfs: pl.DataFrame) -> pl.Series:
    """
    For a long df of pdfs 'values' indexed by 'peaks', transform to wide, one column per peak, and horizontally sum, producing a convoluted signal.

    Return as a Series named 'conv' (convoluted)
    """

    # add a groupwise ordered row index, necessary for pivot
    groupwise_indexed = (
        pdfs
        .with_columns(
            pl.lit(1)
            .alias("row_idx_interm")
            )
        .select(
            pl.col("row_idx_interm")
            .cumcount()
            .over("peak")
            .alias("row_idx"),
            'peak','pdf'
    )
    )  # fmt: skip

    pivoted = groupwise_indexed.pivot(
        index="row_idx", columns="peak", values="pdf"
    ).drop("row_idx")

    convoluted = pivoted.sum_horizontal()
    return convoluted
