"""
fixtures relevent to testing the deconvolution submodule
"""

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
import pytest


@pytest.fixture
def x() -> NDArray[np.float64]:
    """
    an x axis series for computing skewnorms
    """

    return np.linspace(start=-10, stop=10, num=100)


def convoluted_signal(x: NDArray[np.float64]):
    """
    The pdf constructed from the input parameters on x
    """
