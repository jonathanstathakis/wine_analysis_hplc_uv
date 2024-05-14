#!/usr/bin/env python3
"""
The main file of the wine_analysis_hplc_uv thesis project. Will act
as the overarching pipeline to get to final results.
"""

from wine_analysis_hplc_uv.etl.build_library import build_library
import duckdb as db
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.etl.build_library import build_library
import os


def core(data_lib_path: str) -> None:
    """
    Project main file driver function. A pipe to go from start to finish.
    """
    # Phase 1: collect and preprocess data
    data_lib_path = definitions.LIB_DIR
    db_filepath = definitions.DB_PATH

    con = db.connect(db_filepath)
    build_library.build_db_library(
        data_lib_path=data_lib_path,
        con=con,
        ch_m_tblname=definitions.Raw_tbls.CH_META,
        ch_d_tblname=definitions.Raw_tbls.CH_DATA,
        st_tblname=definitions.Raw_tbls.ST,
        ct_tblname=definitions.Raw_tbls.CT,
        sheet_title=os.environ["SAMPLE_TRACKER_SHEET_TITLE"],
        gkey=os.environ["SAMPLE_TRACKER_KEY"],
        ct_un=os.environ["CELLAR_TRACKER_UN"],
        ct_pw=os.environ["CELLAR_TRACKER_PW"],
    )

    # Phase 2: process data

    # peak_alignment_pipe.peak_alignment_pipe(db_path = \
    # '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db')

    # Phase 3: Data Analysis

    # Phase 4: Model Building

    # Phase 5: Results Aggregation and Reporting


def main():
    data_lib_path = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/data/cuprac_data"
    core(data_lib_path)


if __name__ == "__main__":
    main()
