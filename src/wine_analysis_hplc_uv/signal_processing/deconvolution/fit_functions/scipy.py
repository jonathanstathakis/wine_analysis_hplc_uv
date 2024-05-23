"""
Contains fit functions implemented with scipy
"""

from typing import Iterable
import numpy as np
from numpy.typing import NDArray
from numpy import float64
from scipy import stats
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import FloatArray
import logging

logger = logging.getLogger(__name__)


def compute_skewnorm(
    x: Iterable, amp: float, loc: float, scale: float, alpha: float
) -> NDArray[float64]:
    """
    Compute a single skewnorm distribution from input parameters and time interval
    """
    dist = _compute_skewnorm(x=x, params=(amp, loc, scale, alpha))
    return dist


def min_max_scale(x):
    min_x = min(x)
    max_x = max(x)
    return (x - min_x) / (max_x - min_x)


def _compute_skewnorm(
    x: Iterable, params: tuple[float, float, float, float]
) -> NDArray[float64]:
    """
    Calculate a skewnorm distribution along `x` for a given set of parameters `params`

    Use scipy.stats.skewnorm to calculate the pdf, then scale to match the peak maxima.

    :param x: the time interval. An ArrayLike of floats.
    :type x: ArrayLike
    :param params: a four element tuple of parameters necessary to compute the skewnorm.
    amplitude, location, scale, and alpha.
    :type params: tuple[float, float, float, float]
    :return: the pdf calculated along the x interval
    :rtype: NDArray[float64]
    """
    # params container checks
    assert len(params) > 0

    # general params elements checks
    for param in params:
        try:
            float(param)
        except ValueError as e:
            e.add_note(
                f"while validating that param {param} can be cast to float, encountered an error:"
            )
            raise e

    # unpack params for keyword assignment
    amp, loc, scale, alpha = params

    # specific param checks.

    # expect amplitude to be greater than zero
    assert amp > 0

    # expect loc to be within x
    assert min(x) <= loc <= max(x)

    # expect scale to be greater than zero
    assert scale > 0

    # first generate the pdf then calculate it for all values of x
    pdf_ = stats.skewnorm(
        loc=loc,
        scale=scale,
        a=alpha,
    ).pdf(x)

    # scale the output of the pdf to the input amplitude by first scaling it between zero
    # and 1 and then multiplying it by the amplitude.
    skewnorm = amp * min_max_scale(pdf_)

    return skewnorm


def fit_skewnorms(x, *params) -> FloatArray:
    """
    for n peaks in a time window of interval `x`, calculate the convolution as the sum
    of computed skewnorm distributions from input parameters.
    """

    # expect 4 parameters per peak in x.
    if len(params) % 4 != 0:
        raise ValueError(
            "length of params must be divisible by 4\n"
            f"length of params = {len(params)}"
        )

    # Get the number of peaks and reshape for easy indexing
    n_peaks = int(len(params) / 4)
    params = np.reshape(params, (n_peaks, 4))

    # Evaluate each distribution
    logger.info("computing the skewnorm for each param set..")
    dists = [_compute_skewnorm(x, peak_params) for peak_params in params]

    return sum(dists)
