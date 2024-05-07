"""
Test library update execution
"""

from wine_analysis_hplc_uv.etl import update_library
import pytest
import duckdb as db
import tests.definitions as test_defs
import logging
from tests.test_etl.test_post_build_library import gen_sample_test_data

logger = logging.getLogger(__name__)


@pytest.fixture
def con():
    return db.connect(database=test_defs.DB_PATH)


@pytest.mark.parametrize(
    "overwrite, write_to_db",
    [(True, True), (False, True), (True, False), (False, False)],
)
def test_build_library_updater(
    con: db.DuckDBPyConnection,
    gen_sample_cs_wide: gen_sample_test_data.GenSampleCSWide,
    overwrite: bool,
    write_to_db: bool,
):
    sm_output_tblname = "sm_test"
    cs_input_tblname = gen_sample_cs_wide.output_tblname
    cs_output_tblname = "cs_long_test"
    try:
        new_tbls = update_library.update_library(
            con=con,
            overwrite=overwrite,
            write_to_db=write_to_db,
            sm_output_tbname=sm_output_tblname,
            cs_input_tblname=cs_input_tblname,
            cs_output_tblname=cs_output_tblname,
        )
    except Exception as e:
        raise e

    finally:
        logger.debug(f"cleaning up {new_tbls} by dropping from db..")
        for tbl in new_tbls:
            con.execute(f"DROP TABLE {tbl}")
