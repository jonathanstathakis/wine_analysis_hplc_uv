from wine_analysis_hplc_uv.etl.build_library.cellartracker_methods.my_cellartracker_class import (
    MyCellarTracker,
)

import os
import duckdb as db
import logging

logger = logging.getLogger(__name__)


def ct_to_db(con, ct_tbl: str, un: str, pw: str):
    logger.info("ct to db")
    ct = MyCellarTracker(username=un, password=pw)
    ct.to_db(con=con, tbl_name=ct_tbl)


def main():
    con = db.connect(os.path.join(os.path.dirname(__file__), "testdb"))
    ct_tbl = "cellar_tracker"
    un = os.environ["CELLAR_TRACKER_UN"]
    pw = os.environ["CELLAR_TRACKER_PW"]

    ct_to_db(con, ct_tbl, un, pw)


if __name__ == "__main__":
    main()
