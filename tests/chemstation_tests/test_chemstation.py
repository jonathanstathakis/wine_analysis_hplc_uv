"""

"""
import sys

from scipy.integrate._ivp.radau import P

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from mytestmethods.mytestmethods import test_report
import os
from glob import glob
import random
import shutil

from make_test_sample_dir import create_test_pool


def test_chemstation():
    src_dir = get_src_path()
    dst_dir = get_dst_path()
    create_test_pool(src_dir=src_dir, dst_parent_dir=dst_dir)

    tests = []

    # test_report(tests)

    shutil.rmtree(dst_dir)

    return None


def get_src_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/"


def get_dst_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/"


def main():
    test_chemstation()
    return None


if __name__ == "__main__":
    main()
