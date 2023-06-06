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

# def create_sheet(sheet_title: str = "sheet1") -> None:
#     gc = gspread.service_account()
#     print(f"creating {sheet_title}")
#     sh = gc.open_by_key("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY")
#     sh.add_worksheet(sheet_title, 400, 20)
#     return None

"""
Tests of IO, RW of google sheets using gspread.
"""

from gspread_test_methods import get_test_key, test_report
from wine_analysis_hplc_uv.my_sheetsinterface import gspread_methods


def test_gspread_io():
    sheet_title = "test_sampletracker"
    key = get_test_key()
    tests = [(test_connect_to_wksh, key, sheet_title)]

    test_report(tests)


def test_connect_to_wksh(test_key, sheet_title):
    assert gspread_methods.MySheet(test_key, sheet_title)


def main():
    test_gspread_io()


if __name__ == "__main__":
    main()
