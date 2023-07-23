"""
test the following:
- [x] write to db
- [x] string cleaner
"""

import os
import sys
from wine_analysis_hplc_uv import db_methods

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from tests import test_logger
from tests.mytestmethods.mytestmethods import test_report
from tests.mytestmethods import test_methods_df
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.sampletracker import sample_tracker_cleaner
from wine_analysis_hplc_uv.definitions import DB_PATH, ST_TBL_NAME
import pandas as pd


def clean_st_tests(df: pd.DataFrame):
    tests = [(test_sample_tracker_cleaner, df)]
    test_report(tests)
    return None


def get_test_db_path():
    return os.path.join(os.getcwd(), "test_clean_st.db")


def test_sample_tracker_cleaner(df: pd.DataFrame):
    dirty_df = df
    clean_df = sample_tracker_cleaner.sample_tracker_df_cleaner(dirty_df)
    assert not dirty_df.equals(clean_df)
    assert not clean_df.apply(test_methods_df.has_whitespace).any()
    assert not clean_df.apply(test_methods_df.check_uppercase).any()


def main():
    db_path = DB_PATH
    tbl_name = ST_TBL_NAME
    df = db_methods.tbl_to_df(db_filepath=db_path, tblname=tbl_name)
    clean_st_tests(df)


if __name__ == "__main__":
    main()
