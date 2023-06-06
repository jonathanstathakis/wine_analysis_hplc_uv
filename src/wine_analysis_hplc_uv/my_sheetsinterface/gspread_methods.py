import gspread
import os


class MySheet:
    def __init__(self, key, sheet_title):
        gc = get_service_account()
        sh = gc.open_by_key(key)
        wksh = sh.worksheet(sheet_title)


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


# def wksh_to_df(
#     gc,
# ):
#     gc = gspread_methods.get_service_account()

#     sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")

#     sample_tracker_wksh = sh.worksheet(sheet_title)

#     values = sample_tracker_wksh.get_all_values()
#     columns = values[0]
#     data = values[1:]

#     df = pd.DataFrame(data=data, columns=columns)

#     return df
