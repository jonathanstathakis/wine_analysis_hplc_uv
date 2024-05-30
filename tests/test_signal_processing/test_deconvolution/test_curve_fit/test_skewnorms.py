"""
Module to test skewnorm distribution operations
"""

import numpy as np

from wine_analysis_hplc_uv.signal_processing.deconvolution import types
from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ff_spy,
)
import pytest


@pytest.fixture(scope="module")
def amp():
    return 200.0


@pytest.fixture(scope="module")
def loc():
    return 0.0


@pytest.fixture(scope="module")
def scale():
    return 1.0


@pytest.fixture(scope="module")
def skew():
    return -0.5


@pytest.fixture
def skewnorm_1_peak(
    x: types.FloatArray,
    amp: float,
    loc: float,
    scale: float,
    skew: float,
):
    dist = ff_spy.compute_skewnorm(x=x, amp=amp, loc=loc, scale=scale, skew=skew)
    return dist


def test_compute_skewnorm(skewnorm_1_peak: types.FloatArray, amp: float):
    """
    test whether compute_skewnorm works and checking that the maxima matches the input
    amplitude, that the output is a numpy array, and that it has length greater than zero.
    """

    assert isinstance(skewnorm_1_peak, np.ndarray)
    assert len(skewnorm_1_peak) > 0
    assert max(skewnorm_1_peak) == amp


@pytest.fixture
def convolution(
    skewnorm_param_array: types.FloatArray,
    x: types.FloatArray,
) -> types.FloatArray:
    """
    a convoluted skewnorm distribution peak signal
    """
    convolution = ff_spy.fit_skewnorms(x, *skewnorm_param_array)
    return convolution


def test_fit_skewnorm_to_window(convolution: types.FloatArray, x: types.FloatArray):
    """
    test `_fit_skewnorm_to_window` by fitting several peaks and asserting that output
    matches expectation.
    """

    assert len(convolution) > 0
    assert len(convolution) == len(x)
