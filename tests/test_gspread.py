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


def gspread_tests():
    tests = [
        (test_service_account, service_account()),
        (test_sample_tracker_sh, service_account()),
    ]

    test_dicts = [try_pass_fail(func, args) for func, args in tests]

    test_pass_count = sum(test_dict["result"] for test_dict in test_dicts)
    test_fail_count = len(tests) - test_pass_count

    print("")
    print(f"tests passed: {test_pass_count}")
    print(f"tests failed: {test_fail_count}")
    print("")

    print("tests passed:")
    for test in test_dicts:
        if test["result"] == 1:
            print(test["func_name"])

    print("tests failed:")
    for test in test_dicts:
        if test["result"] == 0:
            print(
                f"Test '{test['func_name']}' failed with exception: {test['exception']}"
            )


def try_pass_fail(func, *args, _count=[0], **kwargs):
    _count[0] += 1

    test_dict = dict(func_name=func.__name__, result=0, exception="", value="")

    print(f"test {_count[0]}: {test_dict['func_name']}..", end=" ")

    try:
        test_dict["value"] = func(*args, **kwargs)
    except Exception as e:
        test_dict["exception"] = repr(e)
    else:
        test_dict["result"] = 1

    if test_dict["result"]:
        print(f"passed")
    elif not test_dict["result"]:
        print("failed")

    return test_dict


def service_account():
    return gspread.service_account()


def test_sample_tracker_sh(service_account):
    key = os.environ.get("TEST_SAMPLETRACKER_KEY")
    assert key, "key error"
    assert service_account.open_by_key(
        key
    ), "can't open the service account with the provided key"


def get_sheet_list(sample_tracker_sh):
    sheet_list = sample_tracker_sh.worksheets()
    return sheet_list


def test_service_account(service_account):
    assert service_account


def test_sheet_list(sample_tracker_sh):
    sheet_title = "test_sheet"
    sheet_list = get_sheet_list(sample_tracker_sh)
    assert sheet_list


def test_sheet_title_in_sheet_list(sheet_title: str, sheet_list: list):
    assert sheet_title in sheet_list

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
    gspread_tests()
    return None


if __name__ == "__main__":
    main()
