"""
Test the curve fit submodule
"""

from io import StringIO
import hashlib
import polars as pl
import pytest
import logging
from wine_analysis_hplc_uv.signal_processing.deconvolution.deconvolution import (
    _compute_popt,
    check_in_bounds,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    LBTbl,
    UBTbl,
    P0Tbl,
    ParamDict,
    ParamTbl,
    SkewNormParams2Peaks,
    DataDict,
)

logger = logging.getLogger(__name__)
pl.Config.set_tbl_width_chars(250).set_tbl_cols(100)


def test_skewnorm_param_tbl(skn_param_tbl: SkewNormParams2Peaks):
    """
    test that the param tbl exists
    """

    assert isinstance(skn_param_tbl, pl.DataFrame)
    assert not skn_param_tbl.is_empty()


def test_lb_tbl(lb_tbl: LBTbl):
    """
    test that the lb table exists
    """
    assert isinstance(lb_tbl, pl.DataFrame)
    assert not lb_tbl.is_empty()


def test_ub_tbl(ub_tbl: LBTbl):
    """
    test that the lb table exists
    """
    assert isinstance(ub_tbl, pl.DataFrame)
    assert not ub_tbl.is_empty()


def test_p0_tbl(
    p0_tbl: P0Tbl,
):
    """
    test that the p0 table exists
    """
    assert isinstance(p0_tbl, pl.DataFrame)
    assert not p0_tbl.is_empty()


@pytest.fixture
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


def test_param_tbl(curve_fit_input_params: ParamTbl):
    """
    test that the param table is a polars dataframe and not empty
    """
    assert isinstance(curve_fit_input_params, pl.DataFrame)
    assert not curve_fit_input_params.is_empty()


def test_in_bounds(curve_fit_input_params: ParamTbl):
    curve_fit_input_params.pipe(check_in_bounds)


@pl.api.register_expr_namespace("scale")
class Scaler:
    def __init__(self, expr: pl.Expr):
        self._expr = expr

    def min_max(self) -> pl.Expr:
        return self._expr.sub(self._expr.min()).truediv(
            self._expr.max().sub(self._expr.min())
        )


def _check_popt_in_threshold(df: ParamTbl, threshold: float = 0.05) -> ParamTbl:
    """
    check if the calculated popt column is within a given threshold proportion.
    """

    if not 0 < threshold < 1:
        raise ValueError("threshold should be greater than zero and less than 1")

    df_ = (
        df.with_columns(
            pl.col("actual").scale.min_max(),
            pl.col("popt").scale.min_max(),
        )
        .with_columns(pl.col("popt").sub(pl.col("actual")).abs().alias("diff"))
        .with_columns(pl.col("diff").lt(threshold).alias("in_threshold"))
    )

    if not all(df_.get_column("in_threshold")):
        raise ValueError("popt is below threshold")

    return df_


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


@pytest.fixture
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
        df = curve_fit_input_params.pipe(_compute_popt, x=x, y=y)

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


def test_calculate_popt(
    popt: ParamTbl,
    skn_param_tbl: SkewNormParams2Peaks,
    threshold: float = 0.05,
):
    """
    test the calculation of popt from the input parameters

    the oob test needs to know which peak and param is oob. This space does not currently possess that information. Thus conversion to arrays should not happen until the same scope as the curve fit call.
    """

    # compare the diff to see if within threshold. Takena as the proportion by which the actual is greater than the inferred

    compare_tbl = skn_param_tbl.with_columns(popt.get_column("popt")).rename(
        {"values": "actual"}
    )

    # scale actual and popt to account for negatives

    compare_tbl.pipe(_check_popt_in_threshold, threshold)


def test_nested_dict_to_df(SKEWNORM_PARAMS_2_PEAKS: ParamDict):
    """
    test that `nested_dict_to_df` outputs a polars dataframe
    """
    import tests.test_deconvolution.test_curve_fit.curve_fit_tbls as cft

    df = cft.nested_dict_to_df(
        nested_dict=SKEWNORM_PARAMS_2_PEAKS,
        level_1_colname="peak",
        level_2_colname="param",
    )

    assert isinstance(df, pl.DataFrame)
