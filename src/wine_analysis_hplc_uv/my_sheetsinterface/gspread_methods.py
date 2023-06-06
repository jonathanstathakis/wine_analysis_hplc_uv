import gspread
import os
import pandas as pd


class MySheet:
    def __init__(self, key, sheet_title):
        self.key = key
        self.sheet_title = sheet_title
        self.gc = get_service_account()
        self.sh = self.gc.open_by_key(key)
        self.wksh = self.sh.worksheet(sheet_title)
        self.sheet_df = wksh_to_df(self.wksh)


def get_service_account():
    return gspread.service_account()


def open_worksheet(self, sheet_title: str):
    try:
        wksh = self.sh.worksheet(sheet_title)
    except gspread.exceptions.WorksheetNotFound:
        print(f"Worksheet '{sheet_title}' not found. Creating a new one...")
        wksh = self.sh.add_worksheet(title=sheet_title, rows="100", cols="20")
        print(f"Worksheet '{sheet_title}' created.")
    return wksh


def get_test_st_sh(service_account):
    key = os.environ.get("TEST_SAMPLETRACKER_KEY")
    sh = service_account.open_by_key(key)
    return sh


def get_sheet_list(sample_tracker_sh):
    sheet_list = sample_tracker_sh.worksheets()
    return sheet_list


def wksh_to_df(wksh):
    values = wksh.get_all_values()
    columns = values[0]
    data = values[1:]

    df = pd.DataFrame(data=data, columns=columns)

    return df
