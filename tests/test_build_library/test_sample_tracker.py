import pytest
import duckdb as db
import os
import sys
from wine_analysis_hplc_uv.sampletracker import sample_tracker_processor
from wine_analysis_hplc_uv.df_methods import df_methods
from wine_analysis_hplc_uv.my_sheetsinterface.gspread_methods import WorkSheet
import pandas as pd
from wine_analysis_hplc_uv.sampletracker.st_cleaner import STCleaner
from mydevtools.testing import test_methods_df
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def gsheets_key():
    return os.environ.get("TEST_SAMPLE_TRACKER_KEY")


@pytest.fixture
def sample_tracker(gsheets_key):
    sample_tracker = sample_tracker_processor.SampleTracker(
        sheet_title="test_sample_tracker", key=gsheets_key
    )
    return sample_tracker


@pytest.fixture
def st_test_con():
    con = db.connect()
    return con


@pytest.fixture
def st_tblname():
    return "test_st_tbl"


def test_sampletracker_init(sample_tracker):
    assert sample_tracker


def test_sample_tracker_df(sample_tracker) -> None:
    df_methods.test_df(sample_tracker.df)
    return None


def test_sample_tracker_clean_df(sample_tracker) -> None:
    df1 = sample_tracker.df.copy()
    df_methods.test_df(df1)
    st_cleaner = STCleaner()
    clean_st_df = st_cleaner.clean_st(df1)
    df_methods.test_df(clean_st_df)

    test_methods_df.assert_frame_not_equal(df1, clean_st_df)
    return None


def test_to_sheets(sample_tracker, gsheets_key, sheet_title_2="test_to_sheets"):
    # create sampletracker obj and write to new sheet
    sample_tracker.to_sheets_helper(sheet_title=sheet_title_2)

    # test contents of new sheet
    new_wksh = WorkSheet(key=gsheets_key, sheet_title=sheet_title_2)

    assert sample_tracker.df.equals(new_wksh.sheet_df)
    new_wksh.delete_sheet(new_wksh.wksh)


def test_to_db(sample_tracker, st_test_con, st_tblname):
    sample_tracker.to_db(st_test_con, st_tblname)

    db_df = st_test_con.sql(f"SELECT * FROM {st_tblname}").df()

    pd.testing.assert_frame_equal(sample_tracker.df, db_df)
