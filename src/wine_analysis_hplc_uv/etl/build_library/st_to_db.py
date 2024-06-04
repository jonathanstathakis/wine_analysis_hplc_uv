from wine_analysis_hplc_uv.etl.build_library.sampletracker.sample_tracker_processor import (
    SampleTracker,
)

import duckdb as db
import logging

logger = logging.getLogger(__name__)


def st_to_db(con: db.DuckDBPyConnection, tblname: str, key: str, sheet: str):
    st = SampleTracker(key=key, sheet_title=sheet)
    st.to_db(con=con, tbl_name=tblname)
