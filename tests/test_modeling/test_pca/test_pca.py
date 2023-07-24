import pytest
import logging
import duckdb as db
from wine_analysis_hplc_uv import db_methods, definitions
import wine_analysis_hplc_uv
from wine_analysis_hplc_uv.modeling import pca


@pytest.fixture
def get_con():
    return db.connect(definitions.DB_PATH)


@pytest.fixture
def get_sc_tbl(get_con):
    return pca.get_sc_rel(get_con)


def test_get_sc_tbl(get_sc_tbl):
    assert get_sc_tbl


def test_sc_rel():
    from wine_analysis_hplc_uv.db_methods import db_methods

    con = db.connect(definitions.DB_PATH)
    rel = db_methods.get_sc_rel(con)
    assert not rel.df().empty
