"""

"""
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from mydevtools.testing.mytestmethods import test_report
from wine_analysis_hplc_uv.process_chemstation import uv_extractor
from wine_analysis_hplc_uv.df_methods import df_methods
import os
import shutil
import pandas as pd
import duckdb as db
import rainbow as rb


def test_uv_extractor():
    tests = [(test_uv_extractor,)]
    test_report(tests)


def get_file_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/cuprac/138.D"


def test_uv_extractor():
    """ """
    filepath = get_file_path()

    metadata_dict, data_dict = uv_extractor.uv_extractor(filepath)
    print(metadata_dict)


def main():
    test_uv_extractor()
    return None


if __name__ == "__main__":
    main()
