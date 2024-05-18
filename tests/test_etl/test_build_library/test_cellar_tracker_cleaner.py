from mydevtools.testing import test_methods_df
from wine_analysis_hplc_uv import definitions
import pandas as pd
import pytest
from wine_analysis_hplc_uv.etl.build_library.cellartracker_methods.ct_cleaner import (
    CTCleaner,
)
import logging
import duckdb as db

logging.basicConfig()
logger = logging.getLogger(__name__)


@pytest.fixture
def dirty_ct(testcon: db.DuckDBPyConnection) -> pd.DataFrame:
    df = testcon.sql(f"SELECT * FROM {definitions.Raw_tbls.CT}").df()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    return df


class Cleaned_CT(CTCleaner):
    def __init__(self, dirty_df):
        self.lower_ct = self.lower_collabels(dirty_df)
        self.rename_ct = self.rename_wine_col(self.lower_ct)
        self.replace_vintage_ct = self.replace_vintage_code(self.rename_ct)
        self.html_unescape_ct = self.unescape_name_html(self.replace_vintage_ct)
        self.remove_illegal_chars_ct = self.remove_illegal_chars(self.html_unescape_ct)
        self.wine_col_ct = self.add_wine_col(self.remove_illegal_chars_ct)


@pytest.fixture
def cleaned_ct(dirty_ct):
    cleaned_ct = Cleaned_CT(dirty_ct)
    return cleaned_ct


def test_lower(cleaned_ct):
    has_uppercase = cleaned_ct.lower_ct.columns.to_series().apply(
        test_methods_df.uppercase_in_series
    )
    assert not has_uppercase.all()


def test_rename(cleaned_ct):
    # ensure lower case because df columns already been lowered
    assert "wine" not in cleaned_ct.rename_ct.columns
    assert "name" in cleaned_ct.rename_ct.columns


def test_replace_vintage_code(dirty_ct, cleaned_ct):
    # confirm that 1001 is not in the new df
    assert not cleaned_ct.replace_vintage_ct["vintage"].isin(["1001"]).any()

    index_1001 = dirty_ct[dirty_ct["Vintage"] == "1001"].index
    index_nan = cleaned_ct.replace_vintage_ct[
        cleaned_ct.replace_vintage_ct["vintage"].isna()
    ].index
    assert index_1001.equals(index_nan)


# TODO: add html escape test


def test_has_whitespace(dirty_ct):
    # Apply the function to each column in the DataFrame
    assert not dirty_ct.apply(test_methods_df.has_whitespace).any()


def test_remove_illegal_chars(cleaned_ct):
    # test to ensure that all identified illegal characters are removed - such as single quotes
    cleaned_ct.remove_illegal_chars_ct["name"]
    # str.contains returns a bool series with true if there is a match, assert not to invert it.
    assert not cleaned_ct.remove_illegal_chars_ct["name"].str.contains("'").any()


def test_add_wine_col(cleaned_ct):
    # test whether forming the wine column (a primary key) is successful
    df = cleaned_ct.wine_col_ct
    wine_series = df["vintage"] + " " + df["name"]
    pd.testing.assert_series_equal(df["wine"], wine_series, check_names=False)
