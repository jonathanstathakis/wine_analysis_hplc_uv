"""
Script to create a database containing the output of `tests.test_etl.test_build_library.test_bl.test_build_library`.
Currently (2024-05-13 12:45:01) `test_build_library` is testing on the samples at `tests.data.agilent_D` and as such the comparison database will contain those as well.
"""

import duckdb as db
from pathlib import Path

import logging

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.etl.build_library import build_library
from tests.conftest import BLTestFilePaths

logger = logging.getLogger(__name__)


def create_comparison_database(
    output_db_path: str = BLTestFilePaths.COMPARISON,
    lib_path: str = BLTestFilePaths.SAMPLESET,
):
    # create a connection object to a database at the output path

    try:
        try:
            con = db.connect(output_db_path)
        except Exception:
            raise

        # Write the output of `build_library` to the output db
        try:
            build_library.build_db_library(
                data_lib_path=lib_path,
                con=con,
                sheet_title=definitions.GoogleSheetsAPIInfo.SHEET_TITLE,
                gkey=definitions.GoogleSheetsAPIInfo.GKEY,
                ct_un=definitions.GoogleSheetsAPIInfo.USERNAME,
                ct_pw=definitions.GoogleSheetsAPIInfo.PW,
            )

            assert True
        except Exception:
            raise
        finally:
            # disconnect the db
            con.close()

    except Exception:
        raise


if __name__ == "__main__":
    create_comparison_database()
