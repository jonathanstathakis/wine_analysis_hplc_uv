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

from make_test_sample_dir import create_test_pool


def test_chemstation():
    src_dir = get_src_path()
    dst_dir = get_dst_path()
    create_test_pool(src_dir=src_dir, dst_parent_dir=dst_dir)

    datalibpath = get_dst_path()
    tests = [(test_ChemstationProcessor_init, datalibpath, False)]

    test_report(tests)

    shutil.rmtree(dst_dir)  # clean up sample pool after testing is complete

    return None


def test_ChemstationProcessor_init(datalibpath: str, usepickle: bool):
    assert ChemstationProcessor(datalibpath=datalibpath, usepickle=usepickle)


def get_src_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/"


def get_dst_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/"


def main():
    test_chemstation()
    return None


if __name__ == "__main__":
    main()
