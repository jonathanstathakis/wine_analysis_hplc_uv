import pytest
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_p0,
)


@pytest.fixture(scope="module")
def p0(
    peak_maximas_as_series: pl.Series,
    peak_locs_as_series: pl.Series,
    estimated_peak_widths: pl.Series,
    y,
):
    return gen_p0._compute_p0(
        peak_maximas=peak_maximas_as_series,
        peak_locations=peak_locs_as_series,
        peak_widths=estimated_peak_widths,
    )
