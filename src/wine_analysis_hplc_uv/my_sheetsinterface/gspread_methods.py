"""
2023-06-06 16:12:43 - A set of wrapper classes around gspread for my specific use cases. provides read, and write of sheets in a google sheets workbook through the WorkSheet class (embodies the sheet), and deletion of sheets through the GSheet.delete_sheet() method. Technically WorkSheet has .delete_sheet, but its not the indended usecase atm.

To initialize, call WorkSheet constructor with the Sheet key and intended sheet_title as a string. if the provided title doesnt exist, will open a new one.

To edit sheets, update the sheet_df member object then call write_to_sheet.
"""

import gspread
import os
import pandas as pd


class GSheet:
    def __init__(self, key):
        self.key = key
        self.gc = get_service_account()
        self.sh = self.gc.open_by_key(key)

    def delete_sheet(self, wksh: gspread.Worksheet):
        """
        Delete the target sheet, returns the API response
        """
        response = self.sh.del_worksheet(wksh)
        return response


class WorkSheet(GSheet):
    def __init__(self, key, sheet_title):
        assert isinstance(key, str)
        super().__init__(key)
        self.sheet_title = sheet_title
        self.wksh, self.wksh_response = self.open_worksheet(sheet_title)
        self.sheet_df = wksh_to_df(self.wksh)

    def write_to_sheet(self):
        """
        Update connected sheet with values contained in sheet_df
        """
        df = self.sheet_df
        columns = df.columns.values.tolist()
        data = df.values.tolist()
        values = [columns] + data
        self.wksh.update(values)

    def open_worksheet(self, sheet_title: str):
        response = ""
        try:
            wksh = self.sh.worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            print(f"Worksheet '{sheet_title}' not found. Creating a new one...")
            response = self.sh.add_worksheet(title=sheet_title, rows="100", cols="20")
            print(f"Worksheet '{sheet_title}' created.")
            print(response)
            wksh = self.sh.worksheet(sheet_title)
        return wksh, response


def get_service_account():
    return gspread.service_account()


def get_test_st_sh(service_account):
    key = os.environ.get("TEST_SAMPLETRACKER_KEY")
    sh = service_account.open_by_key(key)
    return sh


def get_sheet_list(sample_tracker_sh):
    sheet_list = sample_tracker_sh.worksheets()
    return sheet_list


def wksh_to_df(wksh):
    """
    get all the values in a provided worksheet as a list of lists.

    if the list of lists is not empty, create a dataframe from values with element 1 as columns, rest as data. If empty, initialize empty dataframe.
    """
    values = wksh.get_all_values()

    if any(values):
        columns = values[0]
        data = values[1:]
        df = pd.DataFrame(data=data, columns=columns)

    else:
        df = pd.DataFrame()

    return df
