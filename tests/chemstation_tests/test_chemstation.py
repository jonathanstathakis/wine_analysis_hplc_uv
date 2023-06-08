"""

"""
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from mytestmethods.mytestmethods import test_report
import os
from glob import glob
import random
import shutil

from wine_analysis_hplc_uv.chemstation.chemstationprocessor import ChemstationProcessor
from wine_analysis_hplc_uv.df_methods import df_methods

from make_test_sample_dir import create_test_pool

from chemstation_tests import (
    chemstation_logger,
    test_logger,
)


def test_chemstation():
    src_dir = get_src_path()
    dst_dir = get_dst_path()
    create_test_pool(src_dir=src_dir, dst_parent_dir=dst_dir)

    datalibpath = get_dst_path()
    ch = ChemstationProcessor(datalibpath=datalibpath, usepickle=False)

    tests = [
        (test_ChemstationProcessor_init, ch),
        (test_metadata_df, ch),
        (test_data_df, ch),
    ]

    test_report(tests)

    shutil.rmtree(dst_dir)  # clean up sample pool after testing is complete

    return None


def test_ChemstationProcessor_init(ch):
    assert ch


def test_metadata_df(ch):
    df_methods.test_df(ch.metadata_df)


def test_data_df(ch) -> None:
    df_methods.describe_df(df=ch.data_df)

    # df_methods.test_df(ch.data_df)


def get_src_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/"


def get_dst_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/"


def main():
    test_chemstation()
    return None


if __name__ == "__main__":
    main()
