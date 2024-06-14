"""
Contains tests for `chapter_one.datasets`
"""

import pytest
import duckdb as db
from wine_analysis_hplc_uv.chapter_one import datasets
import polars as pl


@pytest.fixture(scope="module")
def shiraz(testcon: db.DuckDBPyConnection):
    """
    the raw shiraz dataset as returned by `chapter_one.datasets.get_raw_shiraz`
    """

    shiraz = datasets.get_raw_shiraz(con=testcon)

    return shiraz


def test_get_raw_shiraz(shiraz: pl.DataFrame) -> None:
    """
    test that `get_raw_shiraz` returns a non-empty polars dataframe.
    """

    assert isinstance(shiraz, pl.DataFrame)
    assert not shiraz.is_empty()
