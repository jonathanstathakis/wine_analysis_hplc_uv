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
from mydevtools import project_settings, function_timer as ft
import gspread
import os
import pandas as pd
import os
from wine_analysis_hplc_uv.my_sheetsinterface import gspread_methods as g_methods


from gspread_test_methods import test_report

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


def test_key():
    assert os.environ.get("TEST_SAMPLETRACKER_KEY")


def test_sample_tracker_sh(sheet):
    assert sheet


def test_service_account(service_account):
    assert service_account


def test_sheet_list(sample_tracker_sh):
    sheet_list = g_methods.get_sheet_list(sample_tracker_sh)
    assert sheet_list


def test_sheet_title_in_sheet_list(sheet_title: str, sheet_list: list):
    assert sheet_title in sheet_list


def main():
    test_gspread_connection()
    return None


if __name__ == "__main__":
    main()
