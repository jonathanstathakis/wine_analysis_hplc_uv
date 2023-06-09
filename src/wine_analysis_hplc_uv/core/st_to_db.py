from wine_analysis_hplc_uv.cellartracker_methods.my_cellartracker_class import (
    MyCellarTracker,
)

from wine_analysis_hplc_uv.sampletracker.sample_tracker_processor import SampleTracker

from wine_analysis_hplc_uv.definitions import DB_DIR
import os
import duckdb as db


def st_to_db(db_filepath: str, tbl: str, key: str, sheet: str):
    if not os.path.isfile(DB_DIR):
        con = db.connect(DB_DIR)
        con.close()

    st = SampleTracker(key=key, sheet_title=sheet)
    st.to_db(db_filepath=db_filepath, db_tbl_name=tbl)


def main():
    db_filepath = DB_DIR
    ct_tbl = "sample_tracker"
    key = os.environ.get("SAMPLE_TRACKER_KEY")
    sheet = os.environ.get("SAMPLE_TRACKER_SHEET_TITLE")

    print(sheet, key)
    st_to_db(db_filepath=db_filepath, tbl=ct_tbl, key=key, sheet=sheet)


if __name__ == "__main__":
    main()
