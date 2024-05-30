"""
Test reconstruction of peaks in a signal as pdfs of the skew-norm distribution from a table of parameters
"""

import polars as pl
import pytest
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    ParamTbl,
    FloatArray,
)

from wine_analysis_hplc_uv.signal_processing.deconvolution import (
    deconvolution as deconv,
    fit_assessment,
)


@pytest.fixture(scope="module")
def pdfs(
    x: FloatArray,
    popt: ParamTbl,
):
    return deconv.generate_pdfs(x=x, params=popt)


def test_pdf_generation(
    pdfs: pl.DataFrame,
):
    """
    test whether the generation of the peak signals (pdfs) executes for a set of input parameters (popt)
    """

    # basic tests - exists, not empty

    assert isinstance(pdfs, pl.DataFrame)
    assert not pdfs.is_empty()

    # TODO: add cache for the signals, compare the computed signals against the cache (pdfs)


@pytest.fixture(scope="module")
def reconv(pdfs: pl.DataFrame) -> pl.Series:
    """
    return the reconvoluted pdfs as a Series
    """

    return deconv.convolute_pdfs(pdfs=pdfs)


def test_convolution(reconv: pl.DataFrame):
    """
    test the convolution of an input long dataframe of 'peak', 'values', where 'peak' is the peak index, and 'values' are the pdf of the peak distribution.

    simply test whether the transformationa and aggregation functions execute successfully.
    """

    # compute the convolution

    # expect return value to be a polars series
    assert isinstance(reconv, pl.Series)

    # expect the series to contain values
    assert not reconv.is_empty()


@pytest.fixture(scope="module")
def fit_assessment_input(
    reconv: pl.Series, two_peak_signal_tbl: pl.DataFrame
) -> pl.DataFrame:
    """
    return a dataframe suitable for the fit assessment function input, containing an `x`
    column, `orig` column, and `reconv` column
    """
    return two_peak_signal_tbl.select(
        "x",
        pl.col("y").alias("orig"),
        reconv.alias("reconv"),
    )


@pytest.fixture(scope="module")
def fit_report(fit_assessment_input: pl.DataFrame) -> pl.DataFrame:
    """
    Return the fit assesmment report
    """
    report = fit_assessment.fit_assessment(
        df=fit_assessment_input,
        time_col="x",
        left_signal="orig",
        right_signal="reconv",
    )

    return report


def test_fit_assessment(fit_report: pl.DataFrame):
    """
    TODO: assert df return, not empty..
    """
    assert isinstance(fit_report, pl.DataFrame)


def test_deconvolution() -> pl.DataFrame:
    """
    test the execution of the deconvolution function.
    """
    pass
