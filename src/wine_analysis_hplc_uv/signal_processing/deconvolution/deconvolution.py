"""
Deconvolution
"""

from typing import Sequence
import numpy as np
from scipy import optimize
from scipy.optimize._minpack_py import _lightweight_memoizer, _wrap_func
from typing import Type
import polars as pl
from numpy import float64
from numpy.typing import NDArray
from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ff_spy,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ff_spy,
)


def deconvolution(
    x: Sequence[float],
    y: Sequence[float],
    max_nfev: int = 100,
    verbose_level: int = 2,
):
    """
    deconvolve a signal y with time x into a matrix of single peak signals
    """
    # TODO: calculate the input parameters

    # TODO: fit the signal

    p0 = np.asarray([0, 0, 0, 0])
    bounds = tuple(np.asarray([-1, -1, -1, -1]), np.asarray[1, 1, 1, 1])

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
    x: Sequence[float],
    y: Sequence[float],
    max_nfev: int,
    p0: Sequence[float],
    bounds: tuple[Sequence[float], Sequence[float]],
    verbose_level: int,
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
