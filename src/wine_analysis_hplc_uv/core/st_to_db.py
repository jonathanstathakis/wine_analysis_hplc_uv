from wine_analysis_hplc_uv.cellartracker_methods.my_cellartracker_class import (
    MyCellarTracker,
)

from wine_analysis_hplc_uv.sampletracker.sample_tracker_processor import SampleTracker

from wine_analysis_hplc_uv.definitions import DB_PATH, ST_TBL_NAME
import os
import duckdb as db


def st_to_db(con: str, tblname: str, key: str, sheet: str):
    st = SampleTracker(key=key, sheet_title=sheet)
    st.to_db(con=con, tbl_name=tblname)


def main():
    db_filepath = DB_PATH
    ct_tbl = ST_TBL_NAME
    key = os.environ.get("SAMPLE_TRACKER_KEY")
    sheet = os.environ.get("SAMPLE_TRACKER_SHEET_TITLE")

    print(sheet, key)
    st_to_db(db_filepath=db_filepath, tblname=ct_tbl, key=key, sheet=sheet)


if __name__ == "__main__":
    main()
