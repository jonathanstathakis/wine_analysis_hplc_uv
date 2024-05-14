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

import logging
import os

import duckdb as db
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.etl.build_library import (
    ch_to_db,
    clean_st_to_db,
    st_ct_join,
    st_to_db,
)
from wine_analysis_hplc_uv.etl.build_library.cellartracker_methods import ct_to_db
from wine_analysis_hplc_uv.etl.build_library.cellartracker_methods.ct_cleaner import (
    CTCleaner,
)
from wine_analysis_hplc_uv.etl.build_library.chemstation import ch_m_cleaner

logging_level = logging.INFO
logger = logging.getLogger()
logger.setLevel(logging_level)

# Set up a stream handler to log to the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging_level)
formatter = logging.Formatter(
    "%(asctime)s %(name)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
)
stream_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(stream_handler)


def build_db_library(
    data_lib_path: str,
    con: db.DuckDBPyConnection,
    sheet_title: str,
    gkey: str,
    ct_un: str,
    ct_pw: str,
) -> tuple[definitions.Raw_tbls, definitions.Clean_tbls]:
    """
    Pipeline function to construct the super_table, a cleaned algamation of chemstation,
    sample_tracker and cellartracker tables.

    :return: dict of names of tables created withihn the db
    """

    logger.info("beginning db library build..")

    # check that data lib path exists
    if not os.path.isdir(data_lib_path):
        if not isinstance(data_lib_path, str):
            raise TypeError(f"data_lib_path must be a string")
        else:
            raise ValueError("input path does not contain a directory")

    #  write raw tables to db from sources

    ## chemstation
    ch_to_db.ch_to_db(
        lib_path=data_lib_path,
        mtadata_tbl=definitions.Raw_tbls.CH_META,
        sc_tbl=definitions.Raw_tbls.CH_DATA,
        con=con,
    )

    ## sample_tracker
    st_to_db.st_to_db(
        con=con, tblname=definitions.Raw_tbls.ST, key=gkey, sheet=sheet_title
    )

    ## cellar_tracker
    ct_to_db.ct_to_db(con=con, ct_tbl=definitions.Raw_tbls.CT, un=ct_un, pw=ct_pw)

    ## cleaners

    ## ch_m
    dirty_ch_m_df = con.sql(f"select * from {definitions.Raw_tbls.CH_META}").df()
    ch_m_cleaner_ = ch_m_cleaner.ChMCleaner()
    ch_m_cleaner_.clean_ch_m(dirty_ch_m_df)
    ch_m_cleaner_.to_db(con=con, tbl_name=definitions.Clean_tbls.CH_META)

    ## st
    clean_st_to_db.clean_st_to_db(con)

    ## ct
    raw_ct_df = con.sql(f"SELECT * FROM {definitions.Raw_tbls.CT}").df()
    ct_cleaner = CTCleaner()
    ct_cleaner.clean_df(raw_ct_df)
    ct_cleaner.to_db(con=con, tbl_name=definitions.Clean_tbls.CT)

    # join st with ct to get the primary key then write it back to st for furture joins
    c_st = con.sql(f"SELECT * FROM {definitions.Clean_tbls.ST}").df()
    c_ct = con.sql(f"SELECT * FROM {definitions.Clean_tbls.CT}").df()

    ffk = st_ct_join.FormForeignKeySTCT(c_st, c_ct)
    ffk.write_st_with_foreign_key(con)

    def display_results(con):
        logger.info(con.sql("SELECT table_name FROM duckdb_tables;").df())

        for tbl in con.sql("SELECT table_name FROM duckdb_tables").df()["table_name"]:
            tbl_df = con.sql(f"SELECT * FROM {tbl}").pl()
            logger.info(f"{tbl}\n{tbl_df.describe()}")

    display_results(con)

    return [e.value for e in definitions.Raw_tbls] + [
        e.value for e in definitions.Clean_tbls
    ]


def main():
    data_lib_path = definitions.LIB_DIR
    db_filepath = definitions.DB_PATH

    con = db.connect(db_filepath)

    build_db_library(
        data_lib_path=data_lib_path,
        con=con,
        ch_m_tblname=definitions.Raw_tbls.CH_META,
        ch_d_tblname=definitions.Raw_tbls.CH_DATA,
        st_tblname=definitions.Raw_tbls.ST,
        ct_tblname=definitions.Raw_tbls.CT,
        sheet_title=os.environ.get("SAMPLE_TRACKER_SHEET_TITLE"),
        gkey=os.environ.get("SAMPLE_TRACKER_KEY"),
        ct_un=os.environ.get("CELLAR_TRACKER_UN"),
        ct_pw=os.environ.get("CELLAR_TRACKER_PW"),
    )


if __name__ == "__main__":
    main()
