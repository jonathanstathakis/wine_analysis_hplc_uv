import os
from re import I
from typing import Dict
import pandas as pd
from wine_analysis_hplc_uv.my_sheetsinterface.gspread_methods import WorkSheet


def get_gsheet_key(envar: str = "SAMPLETRACKER_KEY"):
    return os.environ.get(envar)


def get_sample_tracker_wksh(key=get_gsheet_key(), sheet_title="sample_tracker"):
    assert isinstance(key, str)
    wksh = WorkSheet(key=key, sheet_title=sheet_title)
    return wksh


def sample_tracker_df_builder(
    sample_tracker_wksh=get_sample_tracker_wksh(
        key=get_gsheet_key(), sheet_title="sample_tracker"
    )
):
    df = sample_tracker_wksh.sheet_df

    # from the imported range, only select the specified columns

    return df


def st_to_sheets(sample_tracker, sheet_title: str, sudo: bool = False):
    """
    Output df contained in SampleTracker class to google sheets at provided spreadsheet. If no sheet_title is provided, will output to the source sheet, but provide a warning
    """
    key = sample_tracker.wksh.key
    if sudo:
        sheet_title = sample_tracker.sheet_title
        sample_tracker.wksh.sheet_df = sample_tracker.df
        sample_tracker.wksh.write_to_sheet()

    elif sheet_title is None:
        if input(f"no sheet_title provided, write to {sheet_title}? (y/n) ") == "y":
            sheet_title = sample_tracker.sheet_title
            sample_tracker.wksh.sheet_df = sample_tracker.df
            sample_tracker.wksh.write_to_sheet()
        else:
            print("bad input, exiting..\n")
            assert ValueError
    else:
        new_wksh = WorkSheet(key, sheet_title=sheet_title)
        new_wksh.sheet_df = sample_tracker.df
        new_wksh.write_to_sheet()


def main():
    df = sample_tracker_df_builder()
    print(df.head())
    print(df.dtypes)


if __name__ == "__main__":
    main()
