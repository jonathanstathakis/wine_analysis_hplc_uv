import pytest
import os
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.etl.build_library.cellartracker_methods import ct_to_db
import duckdb as db
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


@pytest.fixture
def ct_un():
    return os.environ.get("CELLAR_TRACKER_UN")


@pytest.fixture
def ct_pw():
    return os.environ.get("CELLAR_TRACKER_PW")


@pytest.fixture
def db_con():
    return db.connect()


@pytest.fixture
def ct_tblname():
    return definitions.Raw_tbls.CT


def test_ct_to_db(ct_un, ct_pw, db_con, ct_tblname):
    ct_to_db.ct_to_db(con=db_con, ct_tbl=ct_tblname, pw=ct_pw, un=ct_un)
    tbls_in_db = db_con.sql("SELECT table_name FROM duckdb_tables").df()

    assert ct_tblname in tbls_in_db.values, f"{ct_tblname} not in {tbls_in_db}"
