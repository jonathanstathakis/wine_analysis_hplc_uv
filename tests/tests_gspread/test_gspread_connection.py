"""
A test file of interfacing with google sheets, specifically my sampletracker.

- [x] Set up a seperate workbook that is a linked copy of sampletracker.
$TEST_SAMPLETRACKER_KEY https://docs.google.com/spreadsheets/d/1JKtRQbfV9Bp8i-BDathMJJsy90L2Fj9_yt46qQhYtQU/edit#gid=0
- [ ] test the following:
    - [x] creating service account
    - [x] creating sheet object
    - [ ] obtaining list of sheets in sheet_object
    - [ ] creating worksheet object
    - [ ] read from sheet
    - [ ] add new sheet
    - [ ] write to new sheet
    - [ ] rename sheet
    - [ ] delete sheet
    
This will mimic the sampletracker workflow.

note: cant use pytest as it is generating authorization issues. can refactor at a later date..
"""
from re import I
from venv import create
from mydevtools import project_settings, function_timer as ft
import gspread
import os
import pandas as pd

from gspread_test_methods import test_report
from gspread_tests import (
    test_service_account,
    test_key,
    test_sample_tracker_sh,
    test_sheet_list,
)
from wine_analysis_hplc_uv.my_sheetsinterface.gspread_methods import (
    get_service_account,
    get_test_st_sh,
)


def test_gspread_connection():
    tests = [
        (test_service_account, get_service_account()),
        (test_key, []),
        (test_sample_tracker_sh, get_test_st_sh(get_service_account())),
        (test_sheet_list, get_test_st_sh(get_service_account())),
    ]

    test_report(tests)

    # # st_df = wksh_to_df("sample_tracker")

    # # gc = gspread.service_account()
    # # sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
    # # sh.worksheet(sheet_title).update(
    # #     [st_df.columns.values.tolist()] + st_df.values.tolist()
    # )


# def get_sample_tracker_sheet():
#     gc = gspread.service_account()
#     sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
#     sample_tracker_wksh = sh.worksheet("sample_tracker")


# def wksh_to_df(sheet_title="sheet1"):
#     gc = gspread.service_account()

#     sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")

#     sample_tracker_wksh = sh.worksheet(sheet_title)

#     values = sample_tracker_wksh.get_all_values()
#     columns = values[0]
#     data = values[1:]

#     df = pd.DataFrame(data=data, columns=columns)

#     return df


# def create_sheet(sheet_title: str = "sheet1") -> None:
#     gc = gspread.service_account()
#     print(f"creating {sheet_title}")
#     sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
#     sh.add_worksheet(sheet_title, 400, 20)
#     return None


def main():
    test_gspread_connection()
    return None


if __name__ == "__main__":
    main()
