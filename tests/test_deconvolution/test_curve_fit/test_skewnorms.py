"""
Module to test skewnorm distribution operations
"""

from typing import Sequence
import pytest
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ff_spy,
)
from dataclasses import dataclass


def test_compute_skewnorm(
    x: NDArray[np.float64],
):
    @dataclass
    class Params:
        amp = 200.0
        loc = 0
        scale = 1
        alpha = -0.5

    """
    test whether compute_skewnorm works and checking that the maxima matches the input 
    amplitude, that the output is a numpy array, and that it has length greater than zero.
    """
    dist = ff_spy.compute_skewnorm(
        x=x, amp=Params.amp, loc=Params.loc, scale=Params.scale, alpha=Params.alpha
    )

    assert isinstance(dist, np.ndarray)
    assert len(dist) > 0
    assert max(dist) == Params.amp

    plt.plot(x, dist)
    plt.show()


def test_fit_skewnorm_to_window(x: Sequence):
    """
    test `_fit_skewnorm_to_window` by fitting several peaks and asserting that output
    matches expectation.
    """
    peak_1 = [200, -4, 1, 0.1]
    peak_2 = [400, 2, 2, -0.2]
    params = peak_1 + peak_2

    convolution = ff_spy.fit_skewnorms(x, *params)

    assert len(convolution) > 0
    assert len(convolution) == len(x)
    plt.plot(x, convolution)
    plt.show()
