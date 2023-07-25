"""
Top level file to initialize a wine auth database from scratch.

2023-07-25 10:28:44
Current operations:
1. ch_to_db
2. st_to_db
3. ct_to_db
4. ch_m_cleaner
5. st_cleaner
6. ct_cleaner

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


def build_db_library(data_lib_path: str, con: db.DuckDBPyConnection) -> None:
    """
    Pipeline function to construct the super_table, a cleaned algamation of chemstation, sample_tracker and cellartracker tables.
    """
    # check that data lib path exists
    assert os.path.isdir(data_lib_path), "need an existing directory"

    # 1. create db file if none exists.

    #  3. write raw tables to db from sources
    mtadta_tbl = definitions.CH_META_TBL_NAME
    ch_d_tbl = definitions.CH_DATA_TBL_NAME
    st_tbl = definitions.ST_TBL_NAME
    ct_tbl = definitions.CT_TBL_NAME
    # super_tbl_name = "super_table"

    # chemstation
    ch_to_db.ch_to_db(
        lib_path=data_lib_path, mtadata_tbl=mtadta_tbl, sc_tbl=ch_d_tbl, con=con
    )

    # sample_tracker
    sheet_title = os.environ.get("SAMPLE_TRACKER_SHEET_TITLE")
    gkey = os.environ.get("SAMPLE_TRACKER_KEY")
    st_to_db.st_to_db(con=con, tbl=st_tbl, key=gkey, sheet=sheet_title)

    # cellar_tracker
    un = os.environ.get("CELLAR_TRACKER_UN")
    pw = os.environ.get("CELLAR_TRACKER_PW")
    ct_to_db.ct_to_db(con=con, ct_tbl=ct_tbl, un=un, pw=pw)

    # cleaners
    ## ch_m
    ch_m_cleaner = ChemstationCleaner(db_path=con, raw_tbl_name=mtadta_tbl)
    ch_m_cleaner.to_db(con=con, tbl_name=definitions.CLEAN_CH_META_TBL_NAME)
    ## st
    st_cleaner = STCleaner(con=con, raw_tbl_name=st_tbl)
    st_cleaner.to_db(conth=con, tbl_name=definitions.CLEAN_ST_TBL_NAME)
    ## ct
    raw_ct_df = con.sql(f"SELECT * FROM {ct_tbl}").df()
    ct_cleaner = CTCleaner().clean_df(raw_ct_df)
    ct_cleaner.to_db(con=con, tbl_name=definitions.CLEAN_CT_TBL_NAME)

    return None


def main():
    data_lib_path = definitions.LIB_DIR
    db_filepath = os.path.dirname(os.path.abspath(__file__))

    print(db_filepath)
    # build_db_library(data_lib_path=data_lib_path, db_path=db_filepath)


if __name__ == "__main__":
    main()
