"""
A build library test module. It will primarily be sql-based tests to
observe the shape of the final outcome.

Things to test:

1. 6 tables in the DB
2. The names match expectations.
3. Each table shape matches expectations.

I dont know if this is worth it at the moment tbh. Developing this
from scratch will take time.
"""

import logging
from pathlib import Path

import duckdb as db
import pytest
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.etl.build_library import build_library

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)


from polars import testing as pl_testing


@pytest.fixture
def sample_ch_data_path():
    """
    Return the filepath of the test data
    """
    return "tests/test_data/agilent_D"


def assert_tbls_equal(
    db_1_path: str,
    db_2_path: str,
    tbl_db1: str,
    tbl_db2: str,
) -> None:
    """
    Use polars `testing.assert_frame_equal` on two seperate database tables
    """

    try:
        # connect to both databases
        with db.connect(db_1_path) as con_1, db.connect(db_2_path) as con_2:
            # extract both tables as polars dataframes
            df_1 = con_1.sql(f"SELECT * FROM {tbl_db1}").pl()
            df_2 = con_2.sql(f"SELECT * FROM {tbl_db2}").pl()

            # assert equality
            pl_testing.assert_frame_equal(left=df_1, right=df_2)
    except Exception:
        raise


def test_build_library(bl_test_filepaths, datapaths):
    """
    Test the build library process. test by retrieving all the tables as polars dataframes and checking if they have content, and schemas match expectation.

    TODO: After building the library at `new_db_filepath`, the contents will be tested against the contents of
    """

    try:
        with db.connect(str(bl_test_filepaths.NEW_DB_PATH)) as con:
            tbl_names = build_library.build_db_library(
                data_lib_path=datapaths.SAMPLESET,
                con=con,
                sheet_title=definitions.GoogleSheetsAPIInfo.SHEET_TITLE,
                gkey=definitions.GoogleSheetsAPIInfo.GKEY,
                ct_un=definitions.GoogleSheetsAPIInfo.USERNAME,
                ct_pw=definitions.GoogleSheetsAPIInfo.PW,
            )

        # TODO: test the created tables against a stored dataset to ensure that changes have not modified the output. This will be done by first connecting to both databases, extracting tables with the same names as polars DataFrames and running the assertion

        for tbl in tbl_names:
            assert_tbls_equal(
                db_1_path=bl_test_filepaths.NEW_DB_PATH,
                db_2_path=bl_test_filepaths.COMPARISON,
                tbl_db1=tbl,
                tbl_db2=tbl,
            )

    except Exception as e:
        raise e

    finally:
        # cleanup
        Path(bl_test_filepaths.NEW_DB_PATH).unlink()
