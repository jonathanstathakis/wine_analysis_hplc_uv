import pytest
from polars import testing as ptest
import polars as pl
import duckdb as db
from wine_analysis_hplc_uv.sampletracker import sample_tracker_processor
from tests.my_test_tools.pandas_tools import verify_df
from wine_analysis_hplc_uv.etl.build_library.my_sheetsinterface.gspread_methods import (
    WorkSheet,
)
import pandas as pd
from wine_analysis_hplc_uv.sampletracker.st_cleaner import STCleaner
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def sample_tracker(gsheets_key):
    sample_tracker = sample_tracker_processor.SampleTracker(
        sheet_title="test_sample_tracker", key=gsheets_key
    )
    return sample_tracker


def test_sampletracker_init(sample_tracker):
    assert sample_tracker


def test_sample_tracker_df(sample_tracker) -> None:
    verify_df(sample_tracker.df)
    return None


def test_sample_tracker_clean_df(sample_tracker) -> None:
    df1 = sample_tracker.df.copy()
    verify_df(df1)
    st_cleaner = STCleaner()
    clean_st_df = st_cleaner.clean_st(df1)
    verify_df(clean_st_df)
    ptest.assert_frame_not_equal(pl.from_pandas(df1), pl.from_pandas(clean_st_df))

    return None


def test_to_sheets(sample_tracker, gsheets_key, sheet_title_2="test_to_sheets"):
    # create sampletracker obj and write to new sheet
    sample_tracker.to_sheets_helper(sheet_title=sheet_title_2)

    # test contents of new sheet
    new_wksh = WorkSheet(key=gsheets_key, sheet_title=sheet_title_2)

    assert sample_tracker.df.equals(new_wksh.sheet_df)
    new_wksh.delete_sheet(new_wksh.wksh)


def test_to_db(sample_tracker, st_tblname: str = "test_st_tbl"):
    with db.connect() as con:
        sample_tracker.to_db(con, st_tblname)

        db_df = con.sql(f"SELECT * FROM {st_tblname}").df()

        pd.testing.assert_frame_equal(sample_tracker.df, db_df)
