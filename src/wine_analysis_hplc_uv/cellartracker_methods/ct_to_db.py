from wine_analysis_hplc_uv.cellartracker_methods.my_cellartracker_class import (
    MyCellarTracker,
)

from wine_analysis_hplc_uv.definitions import DB_PATH
import os
import duckdb as db
import logging

logger = logging.getLogger(__name__)


def ct_to_db(con, ct_tbl: str, un: str, pw: str):
    logger.info("ct to db")
    ct = MyCellarTracker(username=un, password=pw)
    ct.to_db(con=con, tbl_name=ct_tbl)


def main():
    db_filepath = DB_PATH
    ct_tbl = "cellar_tracker"
    un = os.environ.get("CELLAR_TRACKER_UN")
    pw = os.environ.get("CELLAR_TRACKER_PW")

    ct_to_db(db_filepath, ct_tbl, un, pw)


if __name__ == "__main__":
    main()
