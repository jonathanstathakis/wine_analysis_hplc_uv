"""
Compare the contents of base chemstation metadata table with sample tracker table to samplecodeentify what cleaning needs to be done to form a union.
"""
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.definitions import DB_PATH, CH_META_TBL_NAME, ST_TBL_NAME
import pandas as pd

import pytest


@pytest.fixture
def get_st_df():
    return db_methods.tbl_to_df(db_filepath=DB_PATH, tblname=ST_TBL_NAME)


@pytest.fixture
def get_ch_m_df():
    return db_methods.tbl_to_df(db_filepath=DB_PATH, tblname=CH_META_TBL_NAME)


@pytest.fixture
def get_st_samplecode_col(get_st_df):
    df = get_st_df
    return df["samplecode"]


@pytest.fixture
def get_ch_m_notebook_col(get_ch_m_df):
    return get_ch_m_df["notebook"]


def test_compare_columns(get_ch_m_notebook_col, get_st_samplecode_col):
    comparison = get_ch_m_notebook_col[
        ~(get_ch_m_notebook_col.isin(get_st_samplecode_col))
    ]
    print(comparison)
    print(comparison.shape)


# def main():
#    compare_columns(col1=st_df["samplecode"], col2=ch_m_df["notebook"])
