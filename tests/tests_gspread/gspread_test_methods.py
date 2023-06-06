"""
Methods for testing gspread.

Contains:

try_pass_fail: a soon-to-be wrapper that takes a function and args, tries to execute it, and reports the status. returns a dict containig:
- func_name: str = "", name of the passed function
- result: bool = 0, 0 for fail, set to 1 for test pass.
- exception: str = "", if fail, error message is stored as a string.
- value: str = "", to store the output of the tested function

test_report:
Takes a list of tuples of `(function object, args)` and runs try_pass_fail on each of them, assembling a list of dicts of the results of the tests, then reports them.

Note: no need to import try_p
"""

import os
from wine_analysis_hplc_uv.my_sheetsinterface import gspread_methods as g_methods
import gspread


def get_test_key():
    return os.environ.get("TEST_SAMPLETRACKER_KEY")


def delete_worksheet(key: str, wksh: gspread.Worksheet):
    gc = g_methods.GSheet(key=key)
    response = gc.delete_sheet(wksh=wksh)
    return response
