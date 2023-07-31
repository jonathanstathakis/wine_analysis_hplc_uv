from wine_analysis_hplc_uv.core import build_library
from wine_analysis_hplc_uv import definitions
import pytest
import os
import duckdb as db
import logging

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)

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


def test_build_library_sample_set(sample_ch_data_path):
    con = db.connect()
    build_library.build_db_library(
        data_lib_path=sample_ch_data_path,
        con=con,
        ch_m_tblname=definitions.CH_META_TBL_NAME,
        ch_d_tblname=definitions.CH_DATA_TBL_NAME,
        st_tblname=definitions.ST_TBL_NAME,
        ct_tblname=definitions.CT_TBL_NAME,
        sheet_title=os.environ.get("SAMPLE_TRACKER_SHEET_TITLE"),
        gkey=os.environ.get("SAMPLE_TRACKER_KEY"),
        ct_un=os.environ.get("CELLAR_TRACKER_UN"),
        ct_pw=os.environ.get("CELLAR_TRACKER_PW"),
    )
