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

note: cant use pytest as it is generating authorization issues. can refactor at a later date..
"""
from re import I
from venv import create
from mydevtools import project_settings, function_timer as ft
import gspread
import os
import pandas as pd


def try_pass_fail(func, *args, **kwargs):
    test_dict = dict(func_name=func.__name__, result=0, exception="", value="")

    try:
        test_dict["value"] = func(*args, **kwargs)
    except Exception as e:
        test_dict["exception"] = str(e)
    else:
        test_dict["result"] = 1

    return test_dict


def gspread_tests():
    tests = [(test_service_account, service_account())]

    test_dicts = [try_pass_fail(func, args) for func, args in tests]

    test_pass_count = sum(test_dict["result"] for test_dict in test_dicts)
    test_fail_count = len(tests) - test_pass_count
    print(f"tests passed: {test_pass_count}")
    print(f"tests failed: {test_fail_count}")
    print("\n")

    for test in test_dicts:
        if test["result"] == 0:
            print(
                f"Test {test['func_name']} failed with exception: {test['exception']}"
            )

    print("tests passed:")
    for test in test_dicts:
        if test["result"] == 1:
            print(test["func_name"], "\n")


def service_account():
    return gspread.service_account()


def test_service_account(service_account):
    assert service_account


def sample_tracker_sh(service_account):
    key = os.environ.get("SAMPLETRACKER_KEY")
    assert key
    return service_account.open_by_key(key)


def get_sheet_list(sample_tracker_sh):
    sheet_list = sample_tracker_sh.worksheets()
    return sheet_list


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
