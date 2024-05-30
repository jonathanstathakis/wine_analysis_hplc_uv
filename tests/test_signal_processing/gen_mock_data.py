"""
module containing functions for mock data generation
"""

from wine_analysis_hplc_uv.signal_processing.deconvolution import types
import numpy as np


def gen_mock_skewnorm_convolution(
    n_peaks: int,
    loc_bounds: tuple[float, float],
    scale_bounds: tuple[float, float],
    skew_bounds: tuple[float, float],
    endpoint_buffer: float,
    seed: float,
) -> types.FloatArray:
    """
    generate a signal as a convolution of skew-normal distributions representing peaks

    :param n_peaks: the number of peaks to include in the signal
    :param loc_bounds: the lower and upper limit on possible locations of peak centroids
    :param scale_bounds: the lower and upper limit of possible scales
    """

    return np.ndarray(shape=0, dtype=np.float64)
