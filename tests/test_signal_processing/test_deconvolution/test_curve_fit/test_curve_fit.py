"""
Test the curve fit submodule
"""

import logging

import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit import curve_fit
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    LBTbl,
    P0Tbl,
    ParamDict,
    ParamTbl,
    SkewNormParams2Peaks,
)

import tests.test_signal_processing.test_deconvolution.test_curve_fit.curve_fit_tbls as cft

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


def test_param_tbl(curve_fit_input_params: ParamTbl):
    """
    test that the param table is a polars dataframe and not empty
    """
    assert isinstance(curve_fit_input_params, pl.DataFrame)
    assert not curve_fit_input_params.is_empty()


def test_in_bounds(curve_fit_input_params: ParamTbl):
    curve_fit_input_params.pipe(curve_fit.check_in_bounds)


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


def test_nested_dict_to_df(skewnorm_params_2_peaks: ParamDict):
    """
    test that `nested_dict_to_df` outputs a polars dataframe
    """

    df = cft.nested_dict_to_df(
        nested_dict=skewnorm_params_2_peaks,
        level_1_colname="peak",
        level_2_colname="param",
    )

    assert isinstance(df, pl.DataFrame)
