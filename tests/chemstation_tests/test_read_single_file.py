"""

"""
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from mydevtools.testing.mytestmethods import test_report
from wine_analysis_hplc_uv.chemstation import read_single_file
from wine_analysis_hplc_uv.df_methods import df_methods
import os
import shutil
import pandas as pd
import duckdb as db
import rainbow as rb


def test_read_single_file():
    tests = [(test_read_single_file,)]
    test_report(tests)


def get_file_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/cuprac/138.D"


def test_read_single_file():
    """ """
    filepath = get_file_path()

    returndict = read_single_file.read_single_file(filepath)
    print(returndict["metadata"])


def main():
    test_read_single_file()
    return None


if __name__ == "__main__":
    main()
