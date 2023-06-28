"""
test the following:
TODO:
- [x] string cleaner
- [x] column renames
- [x] date formatter
- [ ] new_exp_samplecodes
- [ ] remove marked runs.

"""
import re
import os
import sys
from wine_analysis_hplc_uv import db_methods

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from tests import test_logger
from mydevtools.testing.mytestmethods import test_report
from mydevtools.testing import test_methods_df
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.chemstation.ch_m_cleaner import (
    ch_m_cleaner,
    ch_m_date_cleaner,
    ch_m_samplecode_cleaner,
)
from wine_analysis_hplc_uv.definitions import DB_PATH, CH_META_TBL_NAME, ST_TBL_NAME
import dateutil.parser
import pandas as pd


def clean_chm_tests(df: pd.DataFrame):
    tests = [
        # (test_string_cleaner, df),
        # (test_column_renames, df),
        # (test_date_formatter, df),
        # (test_replace_116_sigurd, df),
        # (test_four_digit_samplecode_to_two_digit, df),
        (test_samplecode_cleaner, df),
    ]
    test_report(tests)
    return None


def get_test_db_path():
    return os.path.join(os.getcwd(), "test_clean_ch.db")


def test_string_cleaner(dirty_df: pd.DataFrame):
    """
    test df_cleaning_methods.df_string_cleaner.
    strictly speaking this should be in a seperate test module.

    1. create a copy of the df, then 'clean' it.
    2. assert that the two dfs are different.
    3. assert that the clean_df does not have any trailing whitespace
    4. assert that the clean_df does not have any uppercase characters.
    """
    cp_dirty_df = dirty_df.copy()
    clean_df = df_cleaning_methods.df_string_cleaner(dirty_df)
    assert not cp_dirty_df.equals(clean_df)
    assert not clean_df.apply(test_methods_df.has_whitespace).any()
    assert not clean_df.apply(test_methods_df.check_uppercase).any()


def test_column_renames(dirty_df: pd.DataFrame):
    """
    Function renames the following:
        "notebook": "samplecode", "date": "acq_date", "method": "acq_method"
    """
    cp_dirty_df = dirty_df.copy()
    clean_df = ch_m_cleaner.rename_chemstation_metadata_cols(dirty_df)
    assert not cp_dirty_df.equals(clean_df)
    assert not clean_df.columns.isin(["notebook", "date", "method"]).any()
    assert clean_df.columns.isin(["samplecode", "acq_date", "acq_method"]).any()


def test_date_formatter(dirty_df: pd.DataFrame):
    """ """
    dirty_df = dirty_df.rename({"date": "acq_date"}, axis=1)
    cp_dirty_df = dirty_df.copy()
    clean_df = ch_m_date_cleaner.format_acq_date(dirty_df)
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


def test_four_digit_samplecode_to_two_digit(dirty_df: pd.DataFrame):
    # make copy of original df
    cp_dirty_df = dirty_df.copy()

    # clean the string elements in the df - strip and lower
    clean_df = df_cleaning_methods.df_string_cleaner(dirty_df)

    # col renames
    clean_df = ch_m_cleaner.rename_chemstation_metadata_cols(clean_df)

    # add new_samplecode col as a copy of "samplecode"
    assert isinstance(clean_df, pd.DataFrame)

    clean_df["new_samplecode"] = clean_df["samplecode"]

    # make a copy of the 'new_samplecode' col after cleaning and renaming but before samplecode replacement
    cp_clean_df_new_samplecode = clean_df["new_samplecode"].copy()

    # apply regex to capture samplecodes matching the pattern 0NN1 and extract NN
    clean_df["new_samplecode"] = ch_m_samplecode_cleaner.four_to_two_digit(
        clean_df["new_samplecode"]
    )

    # To test the effectiveness, get the same regex pattern used above
    pattern = ch_m_samplecode_cleaner.get_four_digit_code_regex()

    # check if any codes in the old format are left over
    def match_old_codes(x: str, pattern):
        return bool(pattern.match(x))

    old_code_match = clean_df["new_samplecode"].apply(match_old_codes, args=[pattern])

    # see if any matched
    assert not old_code_match.any()

    # final check, ensure that the copied col isnt equal to the new col
    assert not cp_clean_df_new_samplecode.equals(clean_df["new_samplecode"])


def test_replace_116_sigurd(dirty_df: pd.DataFrame):
    cp_dirty_df = dirty_df.copy()
    clean_df = df_cleaning_methods.df_string_cleaner(dirty_df)
    clean_df = ch_m_cleaner.rename_chemstation_metadata_cols(clean_df)
    clean_df = ch_m_samplecode_cleaner.replace_116_sigurd(clean_df)

    result = clean_df[clean_df["samplecode"] == "sigurdcb"]
    assert not result.empty


def test_samplecode_cleaner(dirty_df: pd.DataFrame):
    """
    Test the individual components of the ch_m_cleaner. The true test is that the difference between the sets of st samplecodes and ch_m samplecodes is zero.
    """
    cp_dirty_df = dirty_df.copy()
    clean_df = df_cleaning_methods.df_string_cleaner(dirty_df)
    clean_df = ch_m_cleaner.rename_chemstation_metadata_cols(clean_df)
    assert "samplecode" in clean_df.columns
    assert isinstance(clean_df, pd.DataFrame)
    clean_df = ch_m_cleaner.ch_m_samplecode_cleaner.ch_m_samplecode_cleaner(clean_df)
    assert (
        clean_df[clean_df["join_samplecode"] == "116"].shape[0] == 1
    ), f"{clean_df[clean_df['samplecode'] == '116']}"
    # check for any change
    assert not cp_dirty_df.equals(clean_df)

    def compare_columns(col1, col2):
        """
        returns elements of Series col1 not in col2
        """
        # returns a boolean series of whether the values of col1 are present anywhere
        # in col2
        set_col1 = set(col1)
        set_col2 = set(col2)

        comparison = set_col1 - set_col2
        return comparison

    # get the values in ch_m.samplecode, not in st.sampelcode
    st_samplecode = db_methods.tbl_to_df(DB_PATH, ST_TBL_NAME, "samplecode")
    ch_m_samplecode = clean_df["join_samplecode"]
    val_in_ch_m_not_st = compare_columns(ch_m_samplecode, st_samplecode)
    print(val_in_ch_m_not_st)

    pd.options.display.max_rows = 200
    print(ch_m_samplecode)
    val_in_st_not_in_ch_m = compare_columns(st_samplecode, ch_m_samplecode)
    print(val_in_st_not_in_ch_m)

    # a is ch_m, b is st, thus difference_ab is elements in a but not b, elements in
    # ch_m but not st. difference_ba is elements in st but not ch_m

    difference_ab = set(ch_m_samplecode).difference(st_samplecode)
    difference_ba = set(st_samplecode).difference(ch_m_samplecode)
    # pandas isin relies on np.in1d with default args. It tests whether each element of
    # the first array is in the second.

    pd_diff_ab = compare_columns(st_samplecode, ch_m_samplecode)

    pd.options.display.max_rows = 200
    # assert val_in_st_not_in_ch_m.shape[0] == 0, f"\nThe following are in st but not in ch_m:\n\n{val_in_st_not_in_ch_m}"


def main():
    db_path = DB_PATH
    tbl_name = CH_META_TBL_NAME
    df = db_methods.tbl_to_df(db_filepath=db_path, tblname=tbl_name)
    clean_chm_tests(df)


if __name__ == "__main__":
    main()
