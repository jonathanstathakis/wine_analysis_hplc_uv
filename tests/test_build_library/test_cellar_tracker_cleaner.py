from mydevtools.testing import test_methods_df
from wine_analysis_hplc_uv.cellartracker_methods import ct_cleaner as cleaner
from wine_analysis_hplc_uv import definitions
import pandas as pd
import pytest
from wine_analysis_hplc_uv.cellartracker_methods.ct_cleaner import CTCleaner


@pytest.fixture
def dirty_ct(con):
    df = con.sql(f"SELECT * FROM {definitions.CT_TBL_NAME}").df()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    return df


class Cleaned_CT(CTCleaner):
    def __init__(self, dirty_df):
        self.lower_ct = self.lower_cols(dirty_df)
        self.rename_ct = self.rename_wine_col(self.lower_ct)
        self.replace_vintage_ct = self.replace_vintage_code(self.rename_ct)
        self.html_unescape_ct = self.unescape_name_html(self.replace_vintage_ct)


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
