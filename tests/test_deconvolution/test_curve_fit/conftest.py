"""
fixtures relevent to testing the deconvolution submodule
"""

import logging
from pathlib import Path

import numpy as np
import polars as pl
import pytest
from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ffspy,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    DataDict,
    FloatArray,
    P0Tbl,
    ParamDict,
    PeakParamDict,
    SkewNormParams2Peaks,
)

from tests.test_deconvolution.test_curve_fit import curve_fit_tbls as cft

logger = logging.getLogger(__name__)


def param_dict_factory(
    amp: float,
    loc: float,
    scale: float,
    skew: float,
) -> dict[str, float]:
    """
    return a dict of the input parameters. A convenience function to provide an ordering to the parameters
    """
    return {"amp": amp, "loc": loc, "scale": scale, "skew": skew}


@pytest.fixture
def TEST_DATA_FILE_TWO_PEAKS() -> str:
    """
    # path to a convoluted 2 peak signal used for tests
    """
    return str(Path(__file__).parent / "data" / "two_peaks.csv")


@pytest.fixture
def SKEWNORM_PARAMS_2_PEAKS() -> ParamDict:
    """
    skewnorm parameters necessary to produce a two peak convolution found in file at TEST_DATA_FILE_TWO_PEAKS
    """
    return {
        "1": param_dict_factory(amp=200, loc=-4, scale=1, skew=0.1),
        "2": param_dict_factory(amp=400, loc=2, scale=2, skew=-0.2),
    }


@pytest.fixture
def PARAMS_2_PEAKS(
    SKEWNORM_PARAMS_2_PEAKS: ParamDict,
) -> dict[str, PeakParamDict | FloatArray]:
    """
    the combination of the peak parameters and sampling point interval 'x'
    """
    return {
        "x": np.linspace(start=-10, stop=10, num=100),
        **SKEWNORM_PARAMS_2_PEAKS,
    }


@pytest.fixture
def x(PARAMS_2_PEAKS: dict[str, PeakParamDict | FloatArray]) -> FloatArray:
    """
    an x axis series for computing skewnorms
    """
    return PARAMS_2_PEAKS["x"]


@pytest.fixture
def skn_param_tbl(SKEWNORM_PARAMS_2_PEAKS) -> SkewNormParams2Peaks:
    """
    return the skewnorm distribution parameters as a tbl
    """
    df = cft.nested_dict_to_df(
        nested_dict=SKEWNORM_PARAMS_2_PEAKS,
        level_1_colname="peak",
        level_2_colname="param",
    )
    return df


@pytest.fixture
def skewnorm_param_array(SKEWNORM_PARAMS_2_PEAKS: ParamDict) -> FloatArray:
    """
    The appended parameter list for the two peaks in the test signal
    """

    def to_float_array(vals):
        return np.asarray(list(vals), dtype=np.float64)

    arr = np.concatenate(
        (
            to_float_array(SKEWNORM_PARAMS_2_PEAKS["1"].values()),
            to_float_array(SKEWNORM_PARAMS_2_PEAKS["2"].values()),
        )
    )
    return arr


@pytest.fixture
def two_peak_signal_tbl(
    x: FloatArray, skewnorm_param_array: FloatArray
) -> pl.DataFrame:
    """
    return the input signal data as a dict
    """

    logger.info("calling fit_skewnorms..")
    # generate a 1d numpy array the length of the x interval
    convolution: FloatArray = ffspy.fit_skewnorms(x, *skewnorm_param_array)

    return pl.DataFrame({"x": x, "y": convolution})


@pytest.fixture
def two_peak_signal(two_peak_signal_tbl: pl.DataFrame) -> DataDict:
    """
    return the signal data as a two member dict
    """
    return {
        "x": np.asarray(two_peak_signal_tbl.get_column("x"), dtype=np.float64),
        "y": np.asarray(two_peak_signal_tbl.get_column("y"), dtype=np.float64),
    }


@pytest.fixture
def cf_tbls(skn_param_tbl: pl.DataFrame, x: FloatArray):
    """
    return a CurveFitParamTbls instance initialised on the `skn_param_tbl`
    """
    return cft.CurveFitParamTbls(input_tbl=skn_param_tbl, x=x)


@pytest.fixture
def p0_tbl(cf_tbls: cft.CurveFitParamTbls) -> P0Tbl:
    """
    return the p0 table attribute from CurveFitParamTbls instance
    """

    return cf_tbls.p0


@pytest.fixture
def lb_tbl(cf_tbls: cft.CurveFitParamTbls) -> P0Tbl:
    """
    return the lb table attribute from CurveFitParamTbls instance
    """

    return cf_tbls.lb


@pytest.fixture
def ub_tbl(cf_tbls: cft.CurveFitParamTbls) -> P0Tbl:
    """
    return the ub table attribute from CurveFitParamTbls instance
    """

    return cf_tbls.ub
