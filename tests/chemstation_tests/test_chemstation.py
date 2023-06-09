"""

"""
import sys
from wine_analysis_hplc_uv.chemstation.chemstation_to_db_methods import (
    chromatogram_spectra_to_db,
)

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from mytestmethods.mytestmethods import test_report
from wine_analysis_hplc_uv.chemstation.chemstationprocessor import ChemstationProcessor
from wine_analysis_hplc_uv.df_methods import df_methods
from wine_analysis_hplc_uv.definitions import LIB_DIR
from make_test_sample_dir import create_test_pool
from chemstation_tests import (
    chemstation_logger,
    test_logger,
)
import os
from glob import glob
import random
import shutil
import pandas as pd


import duckdb as db


def test_chemstation():
    src_dir = get_src_path()
    dst_dir = get_dst_path()
    create_test_pool(src_dir=src_dir, dst_parent_dir=dst_dir)

    # datalibpath = get_dst_path()
    libpath = LIB_DIR
    try:
        ch = ChemstationProcessor(datalibpath=libpath, usepickle=False)
    except Exception as e:
        print(f"{e}")
        shutil.rmtree(dst_dir)  # clean up sample pool after testing is complete

    tests = [
        (test_ChemstationProcessor_init, ch),
        (test_metadata_df, ch),
        (test_data_df, ch),
        (test_data_to_db, ch),
    ]
    test_report(tests)
    shutil.rmtree(dst_dir)  # clean up sample pool after testing is complete
    return None


def test_ChemstationProcessor_init(ch):
    assert ch


def test_metadata_df(ch):
    df_methods.test_df(ch.metadata_df)


def test_data_df(ch) -> None:
    # df_methods.describe_df(df=ch.data_df)

    df_methods.test_df(ch.data_df)


def get_db_filepath():
    return os.path.join(os.getcwd(), "test_ch.db")


def test_data_to_db(ch):
    """
    Write metadata and spectra data to a db table, test whether the input df's match the db table df's:
    - [ ] metadata
    - [ ] data
    """
    db_filepath = get_db_filepath()
    meta_tbl_name = "test_meta_tbl"
    spectra_tbl_name = "test_spectra_tbl"

    ch.to_db(
        db_filepath=db_filepath,
        ch_metadata_tblname=meta_tbl_name,
        ch_sc_tblname=spectra_tbl_name,
    )

    db_metadata_df = None
    db_data_df = None

    with db.connect(db_filepath) as con:
        db_metadata_df = con.sql(f"SELECT * FROM {meta_tbl_name}").df()
        db_data_df = con.sql(f"SELECT * FROM {spectra_tbl_name}").df()

    pd.testing.assert_frame_equal(ch.metadata_df, db_metadata_df)
    pd.testing.assert_frame_equal(ch.data_df, db_data_df)

    os.remove(db_filepath)  # cleanup


def get_src_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/"


def get_dst_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/"


def main():
    test_chemstation()
    return None


if __name__ == "__main__":
    main()
