from wine_analysis_hplc_uv.sampletracker.sample_tracker_processor import SampleTracker

from wine_analysis_hplc_uv import definitions
import os
import duckdb as db
import logging

logger = logging.getLogger(__name__)


def st_to_db(con: db.DuckDBPyConnection, tblname: str, key: str, sheet: str):
    st = SampleTracker(key=key, sheet_title=sheet)
    st.to_db(con=con, tbl_name=tblname)


def main():
    db_filepath = definitions.DB_PATH
    con = db.connect(db_filepath)
    print()

    st_tbl = definitions.Raw_tbls.ST
    key = os.environ.get("SAMPLE_TRACKER_KEY")
    sheet = os.environ.get("SAMPLE_TRACKER_SHEET_TITLE")
    st_to_db(con=con, tblname=st_tbl, key=key, sheet=sheet)


if __name__ == "__main__":
    main()
