"""
test the `compute_popt` function
"""

import pytest
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit import curve_fit
from wine_analysis_hplc_uv.signal_processing.deconvolution import types
from scipy import signal


@pytest.fixture(scope="module")
def peak_widths_as_series(y: types.FloatArray) -> pl.Series:
    """
    measure the widths of peaks present in y using scipy directly
    """

    peaks, _ = signal.find_peaks(x=y)
    results_half = signal.peak_widths(x=y, peaks=peaks, rel_height=0.5)
    widths_ = pl.Series(name="whh", values=results_half[0])
    import matplotlib.pyplot as plt

    def plot_widths(y, peaks, results_half):
        plt.plot(y)
        plt.plot(peaks, y[peaks], "x")
        plt.hlines(*results_half[1:], color="C2")
        plt.show()

    return widths_


@pytest.fixture(scope="module")
def computed_popt(
    x: types.FloatArray,
    y: types.FloatArray,
    peak_maximas_as_series: pl.Series,
    peak_locs_as_series: pl.Series,
    peak_widths_as_series: pl.Series,
) -> types.ParamTbl:
    """
    The popt as computed by the `curve_fit` module
    """

    popt = curve_fit.compute_popt(
        x=x,
        y=y,
        peak_maximas=peak_maximas_as_series,
        peak_locations=peak_locs_as_series,
        peak_widths=peak_widths_as_series,
    )

    return popt


def test_computed_popt_pl_df_not_empty(computed_popt: types.ParamTbl) -> None:
    """
    assert that the `computed_popt` table is a polars dataframe, and not empty. A simple execution test
    """

    assert isinstance(computed_popt, pl.DataFrame)
    assert not computed_popt.is_empty()
