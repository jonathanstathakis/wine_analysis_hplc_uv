"""
A test file of interfacing with google sheets, specifically my sampletracker.

- [ ] Set up a seperate workbook that is a linked copy of sampletracker
- [ ] test the following:
    - [ ] read from sheet
    - [ ] add new sheet
    - [ ] write to new sheet
    - [ ] rename sheet
    - [ ] delete sheet
    
This will mimic the sampletracker workflow.
"""
from re import I
from venv import create
from mydevtools import project_settings, function_timer as ft
import gspread
import os
import pandas as pd
import pytest

b


def testing_gspread():
    sheet_title = "test_sheet"
    sheet_list = get_sheet_list()
    print(sheet_list)

    st_df = wksh_to_df("sample_tracker")

    gc = gspread.service_account()
    sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
    sh.worksheet(sheet_title).update(
        [st_df.columns.values.tolist()] + st_df.values.tolist()
    )


def get_sheet_list():
    gc = gspread.service_account()
    sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
    sheet_list = sh.worksheets()
    return sheet_list


def get_sample_tracker_sheet():
    gc = gspread.service_account()
    sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
    sample_tracker_wksh = sh.worksheet("sample_tracker")


def wksh_to_df(sheet_title="sheet1"):
    gc = gspread.service_account()

    sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")

    sample_tracker_wksh = sh.worksheet(sheet_title)

    values = sample_tracker_wksh.get_all_values()
    columns = values[0]
    data = values[1:]

    df = pd.DataFrame(data=data, columns=columns)

    return df


def create_sheet(sheet_title: str = "sheet1") -> None:
    gc = gspread.service_account()
    print(f"creating {sheet_title}")
    sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
    sh.add_worksheet(sheet_title, 400, 20)
    return None


def main():
    testing_gspread()
    return None


if __name__ == "__main__":
    main()
