"""_summary_

TODO:

- [x] sample_tracker_df_builder
- [x] SampleTracker initialisation
- [x] SampleTracker.df
- [x] SampleTracker.clean_df
- [ ] SampleTracker.st_to_db
- [x] SampleTracker.to_sheets
"""

import os
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st_methods
from wine_analysis_hplc_uv.sampletracker import sample_tracker_processor
from tests.mytestmethods.mytestmethods import test_report
from wine_analysis_hplc_uv.df_methods import df_methods
from wine_analysis_hplc_uv.my_sheetsinterface.gspread_methods import WorkSheet
import pandas as pd


def test_sample_tracker():
    tests = [
        # (test_sample_tracker_df_builder,), # 2023-06-08 16:09:14 deleted this method, instead initializing directly from the wksh member obj.
        (test_sample_tracker_class_init,),
        (test_sample_tracker_df,),
        (test_sample_tracker_clean_df,),
        (test_to_sheets,),
        # (test_to_db, get_SampleTracker(get_key())),
    ]

    test_report(tests)


def get_key():
    return os.environ.get("TEST_SAMPLE_TRACKER_KEY")


def test_sample_tracker_df_builder():
    sample_tracker_df = st_methods.sample_tracker_df_builder()
    assert not sample_tracker_df.empty


def get_SampleTracker(key=get_key()):
    sample_tracker = sample_tracker_processor.SampleTracker(
        sheet_title="test_sample_tracker", key=key
    )
    return sample_tracker


def test_sample_tracker_class_init(key=get_key()):
    st = get_SampleTracker(key)
    return st


def test_sample_tracker_df(key=get_key()) -> None:
    sample_tracker = get_SampleTracker(key=get_key())
    df_methods.test_df(sample_tracker.df)
    return None


def test_sample_tracker_clean_df(key=get_key()) -> None:
    sample_tracker = get_SampleTracker(key=get_key())
    df1 = sample_tracker.df.copy()
    df_methods.test_df(df1)
    sample_tracker.clean_df_helper()
    df2 = sample_tracker.df.copy()
    df_methods.test_df(df2)

    assert not df1.equals(df2)
    return None


def test_to_sheets(key=get_key(), sheet_title_2="test_to_sheets"):
    # create sampletracker obj and write to new sheet
    sample_tracker = get_SampleTracker(key=key)
    sample_tracker.to_sheets_helper(sheet_title=sheet_title_2)

    # test contents of new sheet
    new_wksh = WorkSheet(key=key, sheet_title=sheet_title_2)
    assert sample_tracker.df.equals(new_wksh.sheet_df)
    new_wksh.delete_sheet(new_wksh.wksh)


def get_db_filepath():
    return os.path.join(os.getcwd(), "test_st.db")


def get_db_tbl_name():
    return "test_st_tbl"


def test_to_db(st):
    db_filepath = get_db_filepath()
    db_tbl_name = get_db_tbl_name()
    st.to_db_helper(db_filepath=db_filepath, db_tbl_name=db_tbl_name)

    db_df = None
    import duckdb as db

    with db.connect(db_filepath) as con:
        db_df = con.sql(f"SELECT * FROM {db_tbl_name}").df()
    os.rmtree(db_filepath)  # cleanup

    pd.testing.assert_frame_equal(st.df, db_df)


def main():
    test_sample_tracker()


if __name__ == "__main__":
    main()
