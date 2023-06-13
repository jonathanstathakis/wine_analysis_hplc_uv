"""
Top level file to initialize a wine auth database from scratch.
"""
import os
import shutil

import duckdb as db

from wine_analysis_hplc_uv.core import adapt_super_pipe_to_db
from wine_analysis_hplc_uv.sampletracker import sample_tracker_processor

from wine_analysis_hplc_uv.ux_methods import ux_methods as ux
from wine_analysis_hplc_uv.definitions import DB_DIR, LIB_DIR
import ch_to_db, st_to_db, ct_to_db

import pandas as pd

import logging

chemstation_logger = logging.getLogger("wine_analysis_hplc_uv.chemstation")
chemstation_logger.setLevel(logging.DEBUG)


def build_db_library(data_lib_path: str, db_path: str) -> None:
    """
    Pipeline function to construct the super_table, a cleaned algamation of chemstation, sample_tracker and cellartracker tables.
    """
    assert os.path.isdir(data_lib_path), "need an existing directory"

    # 1. create db file if none exists.
    # dont use context management here because simply opening and closing a connection, forcing the creation of the .db file
    if not os.path.isfile(DB_DIR):
        con = db.connect(DB_DIR)
        con.close()

    #  3. write raw tables to db from sources
    mtadta_tbl = "chemstation_metadata"
    sc_tbl = "chromatogram_spectra"
    st_tbl = "sample_tracker"
    ct_tbl = "cellar_tracker"
    super_tbl_name = "super_table"

    # chemstation
    ch_to_db.ch_to_db(
        lib_path=data_lib_path, mtadata_tbl=mtadta_tbl, sc_tbl=sc_tbl, db_path=db_path
    )

    # sample_tracker
    sheet_title = os.environ.get("SAMPLE_TRACKER_SHEET_TITLE")
    gkey = os.environ.get("SAMPLE_TRACKER_KEY")
    st_to_db.st_to_db(db_filepath=db_path, tbl=st_tbl, key=gkey, sheet=sheet_title)

    # cellar_tracker
    un = os.environ.get("CELLAR_TRACKER_UN")
    pw = os.environ.get("CELLAR_TRACKER_PW")
    ct_to_db.ct_to_db(db_filepath=db_path, ct_tbl=ct_tbl, un=un, pw=pw)

    # # 5. join the tables together.
    # ux.ask_user_and_execute(
    #     "write super table?\n",
    #     adapt_super_pipe_to_db.load_super_table,
    #     get_db_filepath,
    #     table_1=cleaned_chemstation_metadata_table_name,
    #     table_2=cleaned_sampletracker_table_name,
    #     table_3=cleaned_cellartracker_table_name,
    #     tbl_name=super_tbl_name,
    # )
    return None


def remove_existing_db(db_path: str) -> None:
    # remove old db if it exists.
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"deleted {db_path}")
    return None


def main():
    data_lib_path = LIB_DIR
    db_filepath = DB_DIR
    build_db_library(data_lib_path=data_lib_path, db_path=db_filepath)


if __name__ == "__main__":
    main()
