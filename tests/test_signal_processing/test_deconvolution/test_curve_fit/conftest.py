"""
fixtures relevent to testing the deconvolution submodule
"""

import hashlib
import logging
import random
from io import StringIO
from pathlib import Path

import numpy as np
import polars as pl
import pytest
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit import curve_fit
from wine_analysis_hplc_uv.signal_processing.deconvolution.fit_functions import (
    scipy as ffspy,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    DataDict,
    FloatArray,
    LBTbl,
    P0Tbl,
    ParamDict,
    ParamTbl,
    PeakParamDict,
    SkewNormParams2Peaks,
    UBTbl,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution import types

from tests.test_signal_processing.test_deconvolution.test_curve_fit import (
    curve_fit_tbls as cft,
)

logger = logging.getLogger(__name__)


class HashObjects:
    def gen_hash(self, input) -> str:
        return hashlib.sha256(input).hexdigest()

    def _encode_str(self, string) -> bytes:
        return string.encode(encoding="UTF-8", errors="strict")

    def _df_to_hash_bytes(self, df: pl.DataFrame) -> bytes:
        return self._encode_str(str(df.hash_rows()))

    def df_to_hash(self, df: pl.DataFrame) -> str:
        """
        convert a polars dataframe to a deterministic hash string
        """
        return self.gen_hash(self._df_to_hash_bytes(df=df))

    def dfs_to_hash(self, dfs: list[pl.DataFrame]) -> str:
        """
        convert a list of polars dataframes to a deterministic hash string
        """
        hashes = [self.df_to_hash(df) for df in dfs]
        return hashlib.sha256(self._encode_str(str(hashes))).hexdigest()


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


@pytest.fixture(scope="module")
def skewnorm_params_2_peaks() -> ParamDict:
    """
    skewnorm parameters necessary to produce a two peak convolution found in file at TEST_DATA_FILE_TWO_PEAKS
    """
    return {
        "1": param_dict_factory(amp=200.0, loc=-4.0, scale=1.0, skew=0.1),
        "2": param_dict_factory(amp=400.0, loc=2.0, scale=2.0, skew=-0.2),
    }


def extract_param_from_dict(
    param_dict: dict,
    param: str,
) -> pl.Series:
    """
    extract a given parameter from the param dict
    """

    parameters = []

    for v in param_dict.values():
        for k, vv in v.items():
            if k == param:
                parameters.append(vv)

    param_series = pl.Series(name=param, values=parameters)

    return param_series


@pytest.fixture(scope="module")
def peak_maximas_as_series(skewnorm_params_2_peaks: types.ParamDict) -> pl.Series:
    """
    The simulated signal peak maximas as a polars series
    """
    maximas = extract_param_from_dict(skewnorm_params_2_peaks, "amp")
    return maximas


@pytest.fixture(scope="module")
def peak_locs_as_series(skewnorm_params_2_peaks: types.ParamDict) -> pl.Series:
    """
    The simulated signal peak locs as a polars series
    """
    locs = extract_param_from_dict(skewnorm_params_2_peaks, "loc")
    return locs


@pytest.fixture(scope="module")
def peak_scales_as_series(skewnorm_params_2_peaks: types.ParamDict) -> pl.Series:
    """
    The simulated signal peak scales as a polars series
    """
    scales = extract_param_from_dict(skewnorm_params_2_peaks, "scale")
    return scales


@pytest.fixture(scope="module")
def peak_skews_as_series(skewnorm_params_2_peaks: types.ParamDict) -> pl.Series:
    """
    The simulated signal peak maximas as a polars series
    """
    skews = extract_param_from_dict(skewnorm_params_2_peaks, "skew")
    return skews


@pytest.fixture(scope="module")
def PARAMS_2_PEAKS(
    skewnorm_params_2_peaks: ParamDict,
) -> dict[str, PeakParamDict | FloatArray]:
    """
    the combination of the peak parameters and sampling point interval 'x'
    """
    return {
        "x": np.linspace(start=0, stop=10, num=100),
        **skewnorm_params_2_peaks,
    }


@pytest.fixture(scope="module")
def x(PARAMS_2_PEAKS: dict[str, PeakParamDict | FloatArray]) -> FloatArray:
    """
    an x axis series for computing skewnorms
    """

    return PARAMS_2_PEAKS["x"]


@pytest.fixture(scope="module")
def skn_param_tbl(skewnorm_params_2_peaks) -> SkewNormParams2Peaks:
    """
    return the skewnorm distribution parameters as a tbl
    """
    df = cft.nested_dict_to_df(
        nested_dict=skewnorm_params_2_peaks,
        level_1_colname="peak",
        level_2_colname="param",
    )
    return df


@pytest.fixture(scope="module")
def skewnorm_param_array(skewnorm_params_2_peaks: types.ParamDict) -> types.FloatArray:
    """
    The appended parameter list for the two peaks in the test signal
    """

    def to_float_array(vals):
        return np.asarray(list(vals), dtype=np.float64)

    arr = np.concatenate(
        (
            to_float_array(skewnorm_params_2_peaks["1"].values()),
            to_float_array(skewnorm_params_2_peaks["2"].values()),
        )
    )
    return arr


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
def y(two_peak_signal_tbl: pl.DataFrame) -> FloatArray:
    """
    a signal containing two peaks
    """

    return np.asarray(two_peak_signal_tbl.get_column("y"), dtype=np.float64)


@pytest.fixture(scope="module")
def two_peak_signal(two_peak_signal_tbl: pl.DataFrame) -> DataDict:
    """
    return the signal data as a two member dict
    """
    return {
        "x": np.asarray(two_peak_signal_tbl.get_column("x"), dtype=np.float64),
        "y": np.asarray(two_peak_signal_tbl.get_column("y"), dtype=np.float64),
    }


@pytest.fixture(scope="module")
def cf_tbls(skn_param_tbl: pl.DataFrame, x: FloatArray):
    """
    return a CurveFitParamTbls instance initialised on the `skn_param_tbl`
    """
    return cft.CurveFitParamTbls(input_tbl=skn_param_tbl, x=x)


@pytest.fixture(scope="module")
def p0_tbl(cf_tbls: cft.CurveFitParamTbls) -> P0Tbl:
    """
    return the p0 table attribute from CurveFitParamTbls instance
    """

    return cf_tbls.p0


@pytest.fixture(scope="module")
def lb_tbl(cf_tbls: cft.CurveFitParamTbls) -> P0Tbl:
    """
    return the lb table attribute from CurveFitParamTbls instance
    """

    return cf_tbls.lb


@pytest.fixture(scope="module")
def ub_tbl(cf_tbls: cft.CurveFitParamTbls) -> P0Tbl:
    """
    return the ub table attribute from CurveFitParamTbls instance
    """

    return cf_tbls.ub


@pytest.fixture(scope="module")
def curve_fit_input_params(
    lb_tbl: LBTbl,
    ub_tbl: UBTbl,
    p0_tbl: P0Tbl,
) -> ParamTbl:
    """
    a table consisting of the peak idx, param name, p0, lb, and ub input to curve fit
    """

    # concatenate the peak tables.
    # each table has a peak column, parameter name column and paramter value column

    # combine the intermediates together widthwise
    df = pl.concat([lb_tbl, p0_tbl, ub_tbl], how="align")

    # add a param_order column to maintain parameter order
    order_df = pl.DataFrame(
        {"param_order": [0, 1, 2, 3], "param": ["amp", "loc", "scale", "skew"]}
    )
    df = df.join(order_df, on="param")

    # order the df to be more rational
    df = df.sort(by=["peak", "param_order"])
    df = df.select(["peak", "param", "param_order", "lb", "p0", "ub"])

    return df


@pytest.fixture(scope="module")
def popt(
    curve_fit_input_params: ParamTbl,
    two_peak_signal: DataDict,
    request,
):
    """
    provide the popt for the input params and signal
    """

    def df_from_str_json(json_str: str):
        return pl.read_json(StringIO(json_str))

    def df_to_json_str(df: pl.DataFrame) -> str:
        return df.write_json()

    def set_cache_initial_state(
        x, y, request, input_params_hash: str, hash_key: str, df_key: str
    ) -> pl.DataFrame:
        # return a df as ParamTbl with the bounds and initial guess alongside the popt
        df = curve_fit_input_params.pipe(curve_fit.compute_popt, x=x, y=y)

        logger.info("no popt cache detected, setting now..")
        # set the hash
        request.config.cache.set(hash_key, input_params_hash)

        # set the object
        request.config.cache.set(df_key, df_to_json_str(df))

        return df

    hash_key = "input_hash"
    df_key = "popt_df"

    # hash the output
    hasher = HashObjects()

    input_params_hash = hasher.dfs_to_hash(
        dfs=[curve_fit_input_params, pl.DataFrame(two_peak_signal)]
    )

    # get the stored cache, if none, write to cache and continue
    cached_hash = request.config.cache.get(hash_key, None)

    # if no hash, set initial state

    x = two_peak_signal["x"]
    y = two_peak_signal["y"]

    if not cached_hash:
        df = set_cache_initial_state(
            x=x,
            y=y,
            request=request,
            input_params_hash=input_params_hash,
            hash_key=hash_key,
            df_key=df_key,
        )
        return df

    else:
        # compare the cached hash to the current hash, if they dont match, raise an error.
        try:
            if input_params_hash != cached_hash:
                raise ValueError(
                    "popt hashes dont match, hash generated from popt_df has changed!"
                )
            else:
                logger.info("retrieving popt tbl from cache..")
                json_str = request.config.cache.get(df_key, None)
                df = df_from_str_json(json_str)
        except ValueError as e:
            e.add_note("clearing cache..")
            request.config.cache.set(hash_key, None)
            request.config.cache.set(df_key, None)
            raise e

    return df


def calculate_random_array(a, b, n):
    """
    calculate a numpy array of random float values within the bounds `a` and `b` of
    length `n`. Using the built-in `random.uniform` because the numpy seeding appears
    complicated. can swap to numpy later if i figure it out.
    """

    return np.asarray([random.uniform(a=a, b=b) for x in range(n)])


@pytest.fixture(scope="module")
def n_peaks_mock():
    """
    number of peaks in the mock dataset
    """

    return 5


@pytest.fixture(scope="module")
def mock_amp_bounds() -> tuple[float, float]:
    """
    define the minimum and maximum amplitudes of the peaks
    """
    return (0, 100)


@pytest.fixture(scope="module")
def mock_peak_maximas(
    n_peaks_mock: int, mock_amp_bounds: tuple[float, float]
) -> pl.Series:
    """
    compute the peak maximas as random floats between the bounds
    """
    return pl.Series(
        name="amp",
        values=calculate_random_array(
            a=mock_amp_bounds[0], b=mock_amp_bounds[1], n=n_peaks_mock
        ),
    )


@pytest.fixture(scope="module")
def mock_loc_bounds(x: types.FloatArray):
    """
    the location bounds of the mock peak data
    """
    return min(x), max(x)


@pytest.fixture(scope="module")
def mock_peak_locs(n_peaks_mock, mock_loc_bounds: tuple[float, float]) -> pl.Series:
    """
    create random peak locations by generating an array of random values then sorting.
    """

    loc = pl.Series(
        name="loc",
        values=calculate_random_array(
            a=mock_loc_bounds[0], b=mock_loc_bounds[1], n=n_peaks_mock
        ),
    ).sort()
    return loc


@pytest.fixture(scope="module")
def peak_width_bounds(x: types.FloatArray) -> tuple[float, float]:
    """
    define the minimum and maximum half height widths for the peaks
    """
    x_range = max(x) - min(x)
    lb = x_range / 10
    ub = x_range / 5
    bounds = (lb, ub)
    return bounds


@pytest.fixture(scope="module")
def mock_peak_widths(
    n_peaks_mock: int, peak_width_bounds: tuple[float, float]
) -> pl.Series:
    """
    create random widths for n peaks within the provided bounds
    """

    return pl.Series(
        name="scale",
        values=calculate_random_array(
            a=peak_width_bounds[0], b=peak_width_bounds[1], n=n_peaks_mock
        ),
    )


@pytest.fixture(scope="module")
def mock_skews(n_peaks_mock: int) -> pl.Series:
    """
    return a polars series of zeroes with length equal to n_peaks
    """

    return pl.Series(np.zeros(shape=n_peaks_mock))
