"""
test the following:
TODO:
- [x] string cleaner
- [x] column renames
- [x] date formatter
- [ ] new_ids
- [ ] remove marked runs.
"""
import re
import os
import sys
from wine_analysis_hplc_uv import db_methods

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from tests import test_logger
from tests.mytestmethods.mytestmethods import test_report
from tests.mytestmethods import test_methods_df
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.chemstation import ch_metadata_tbl_cleaner
from wine_analysis_hplc_uv.definitions import DB_PATH, CH_META_TBL_NAME
import dateutil.parser
import pandas as pd


def clean_chm_tests(df: pd.DataFrame):
    tests = [
        (test_string_cleaner, df),
        (test_column_renames, df),
        (test_date_formatter, df),
    ]
    test_report(tests)
    return None


def get_test_db_path():
    return os.path.join(os.getcwd(), "test_clean_ch.db")


def test_string_cleaner(df: pd.DataFrame):
    dirty_df = df
    clean_df = df_cleaning_methods.df_string_cleaner(dirty_df)
    assert not dirty_df.equals(clean_df)
    assert not clean_df.apply(test_methods_df.has_whitespace).any()
    assert not clean_df.apply(test_methods_df.check_uppercase).any()


def test_column_renames(dirty_df: pd.DataFrame):
    """
    Function renames the following: "notebook": "id", "date": "acq_date", "method": "acq_method"
    """
    clean_df = ch_metadata_tbl_cleaner.rename_chemstation_metadata_cols(dirty_df)
    assert not dirty_df.equals(clean_df)
    assert not clean_df.columns.isin(["notebook", "date", "method"]).any()
    assert clean_df.columns.isin(["id", "acq_date", "acq_method"]).any()


def test_date_formatter(dirty_df: pd.DataFrame):
    """ """
    dirty_df = dirty_df.rename({"date": "acq_date"}, axis=1)
    cp_dirty_df = dirty_df.copy()
    clean_df = ch_metadata_tbl_cleaner.format_acq_date(dirty_df)
    # assert not dirty_df["acq_date"].equals(clean_df["acq_date"]), "no change"
    assert not cp_dirty_df["acq_date"].equals(
        clean_df["acq_date"]
    )  # check if any change

    # Check each timestamp in the transformed column matches the new format
    pattern = re.compile(
        "^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
    )  # The pattern matches 'YYYY-MM-DD HH:MM:SS'
    # check_format = pattern.match("13-Apr-23, 13:32:12")
    check_format = clean_df["acq_date"].apply(lambda x: bool(pattern.match(x)))

    assert check_format.all(), "format doesnt match '%Y-%m-%d, %H:%M:%S'"


def main():
    db_path = DB_PATH
    tbl_name = CH_META_TBL_NAME
    df = db_methods.tbl_to_df(db_filepath=db_path, tblname=tbl_name)
    clean_chm_tests(df)


if __name__ == "__main__":
    main()
