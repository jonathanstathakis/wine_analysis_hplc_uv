"""
Test the generation of the curve fit parameter table
"""

import pytest
import numpy as np
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution import (
    types,
)
from wine_analysis_hplc_uv.signal_processing.deconvolution.curve_fit.curve_fit_params import (
    gen_curve_fit_params,
)


@pytest.fixture(scope="module")
def param_tbl(
    x: types.FloatArray,
    mock_peak_maximas: pl.Series,
    mock_peak_locs: pl.Series,
    mock_peak_widths: pl.Series,
) -> pl.DataFrame:
    """
    the parameter table, lb, p0, ub
    """

    param_tbl = gen_curve_fit_params.compute_curve_fit_params(
        x=pl.Series(name="x", values=x),
        peak_maximas=mock_peak_maximas,
        peak_locations=mock_peak_locs,
        peak_widths=mock_peak_widths,
    )

    return param_tbl


def test_param_tbl_is_pl_df_not_empty(param_tbl: pl.DataFrame) -> None:
    """
    test if the param_tbl generated by `_compute_curve_fit_params` is a polars dataframe, and is not empty
    """
    assert isinstance(param_tbl, pl.DataFrame)
    assert not param_tbl.is_empty()


@pytest.fixture
def p0_extracted(param_tbl: pl.DataFrame) -> types.FloatArray:
    """
    p0 as extracted from the param_tbl
    """
    p0 = gen_curve_fit_params._extract_p0(param_tbl=param_tbl)
    return p0


def test_extract_p0_is_float_array_not_empty(p0_extracted: types.FloatArray) -> None:
    """
    test whether `p0_extracted` is a numpy float array and not empty
    """
    assert isinstance(p0_extracted, np.ndarray)
    assert p0_extracted.dtype == np.float64
    assert p0_extracted.size


@pytest.fixture
def bounds_extracted(
    param_tbl: pl.DataFrame,
) -> tuple[types.FloatArray, types.FloatArray]:
    """
    the bounds as extracted from the param_tbl
    """
    bounds = gen_curve_fit_params._extract_bounds(param_tbl=param_tbl)
    return bounds


def test_extract_bounds_is_tuple_float_array_not_empty(
    bounds_extracted: tuple[types.FloatArray, types.FloatArray],
) -> None:
    """
    test whether `bounds_extracted` is a tuple of numpy float array and not empty
    """
    assert isinstance(bounds_extracted, tuple)

    for x in bounds_extracted:
        assert isinstance(x, np.ndarray)
        assert x.dtype == np.float64
        assert x.size


@pytest.fixture
def extracted_params(
    param_tbl: pl.DataFrame,
) -> tuple[types.FloatArray, tuple[types.FloatArray, types.FloatArray]]:
    """
    The return from `extract_params` ready for input into `curve_fit`
    """
    params = gen_curve_fit_params.extract_params(param_tbl=param_tbl)

    return params


def test_extract_params_dtypes_not_empty(
    extracted_params: tuple[
        types.FloatArray, tuple[types.FloatArray, types.FloatArray]
    ],
) -> None:
    """
    test if the param columns are correctly extracted from the `param_tbl`
    """
    assert isinstance(extracted_params, tuple)
    assert len(extracted_params) == 2
    # p0
    assert isinstance(extracted_params[0], np.ndarray)
    assert extracted_params[0].dtype == np.float64
    assert extracted_params[0].size

    # bounds
    assert isinstance(extracted_params[1], tuple)
    assert len(extracted_params[1]) == 2

    for x in extracted_params[1]:
        assert isinstance(x, np.ndarray)
        assert x.dtype == np.float64
        assert x.size