import gspread
import os


def get_service_account():
    return gspread.service_account()


def get_test_st_sh(service_account):
    key = os.environ.get("TEST_SAMPLETRACKER_KEY")
    sh = service_account.open_by_key(key)
    return sh


def get_sheet_list(sample_tracker_sh):
    sheet_list = sample_tracker_sh.worksheets()
    return sheet_list
