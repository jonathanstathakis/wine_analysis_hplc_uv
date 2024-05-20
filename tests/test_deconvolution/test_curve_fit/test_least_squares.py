"""
Test least_squares implementation
"""

from wine_analysis_hplc_uv.signal_processing.deconvolution import (
    deconvolution as deconv,
)


def test_least_squares():
    """
    test least_squares as successfully optimizing the fit based on input parameters. output will be compared to the parameters used to generate the pdf.
    """
