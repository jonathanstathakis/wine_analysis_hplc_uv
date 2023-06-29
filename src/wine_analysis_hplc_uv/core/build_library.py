"""
Top level file to initialize a wine auth database from scratch.
"""
import os
import shutil

import duckdb as db

from wine_analysis_hplc_uv.core import adapt_super_pipe_to_db
from wine_analysis_hplc_uv.sampletracker.st_cleaner import STCleaner
from wine_analysis_hplc_uv.chemstation.ch_m_cleaner.ch_m_cleaner import (
    ChemstationCleaner,
)
from wine_analysis_hplc_uv.cellartracker_methods.ct_cleaner import CTCleaner
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.core import ch_to_db, st_to_db, ct_to_db
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
    if not os.path.isfile(db_path):
        con = db.connect(db_path)
        con.close()

    #  3. write raw tables to db from sources
    mtadta_tbl = definitions.CH_META_TBL_NAME
    ch_d_tbl = definitions.CH_DATA_TBL_NAME
    st_tbl = definitions.ST_TBL_NAME
    ct_tbl = definitions.CT_TBL_NAME
    # super_tbl_name = "super_table"

    # chemstation
    ch_to_db.ch_to_db(
        lib_path=data_lib_path, mtadata_tbl=mtadta_tbl, sc_tbl=ch_d_tbl, db_path=db_path
    )

    # sample_tracker
    sheet_title = os.environ.get("SAMPLE_TRACKER_SHEET_TITLE")
    gkey = os.environ.get("SAMPLE_TRACKER_KEY")
    st_to_db.st_to_db(db_filepath=db_path, tbl=st_tbl, key=gkey, sheet=sheet_title)

    # cellar_tracker
    un = os.environ.get("CELLAR_TRACKER_UN")
    pw = os.environ.get("CELLAR_TRACKER_PW")
    ct_to_db.ct_to_db(db_filepath=db_path, ct_tbl=ct_tbl, un=un, pw=pw)

    # cleaners
    ## ch_m
    ch_m_cleaner = ChemstationCleaner(db_path=db_path, raw_tbl_name=mtadta_tbl)
    ch_m_cleaner.to_db(db_filepath=db_path, tbl_name=definitions.CLEAN_CH_META_TBL_NAME)
    ## st
    st_cleaner = STCleaner(db_path=db_path, raw_tbl_name=st_tbl)
    st_cleaner.to_db(db_filepath=db_path, tbl_name=definitions.CLEAN_ST_TBL_NAME)
    ## ct
    ct_cleaner = CTCleaner(db_path=db_path, raw_tbl_name=ct_tbl)
    ct_cleaner.to_db(db_filepath=db_path, tbl_name=definitions.CLEAN_CT_TBL_NAME)

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
    data_lib_path = definitions.LIB_DIR
    db_filepath = os.path.dirname(os.path.abspath(__file__))

    print(db_filepath)
    # build_db_library(data_lib_path=data_lib_path, db_path=db_filepath)


if __name__ == "__main__":
    main()
