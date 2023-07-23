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
from tests.mytestmethods.mytestmethods import test_report
from gspread_test_methods import get_test_key, delete_worksheet
from wine_analysis_hplc_uv.my_sheetsinterface import gspread_methods


def test_gspread_io():
    tests = [
        (test_connect_to_wksh, orig_sampletracker_wksh()),
        (test_wksh_to_df, orig_sampletracker_wksh()),
        (test_create_new_sheet,),
        (test_write_to_new_sheet,),
        (test_delete_sheet,),
        (test_new_written_sheet_eq_source,),
    ]

    test_report(tests)


def test_connect_to_wksh(mysheet_class):
    assert mysheet_class


def orig_sampletracker_wksh(
    key=get_test_key(), sheet_title: str = "test_sample_tracker"
):
    assert isinstance(key, str)
    return gspread_methods.WorkSheet(key=key, sheet_title=sheet_title)


def test_wksh_to_df(wksh):
    df = wksh.df

    assert not df.empty, "DataFrame is empty"

    assert not df.isnull().values.any(), "DataFrame contains NaN values"

    assert (
        len(df.drop_duplicates()) > 1
    ), "DataFrame does not have more than one unique row"


def new_worksheet_class(key=get_test_key(), sheet_title="test_new_sheet"):
    return gspread_methods.WorkSheet(key, sheet_title)


def test_create_new_sheet(sheet_title="test_new_sheet_create"):
    new_wksh = new_worksheet_class(sheet_title=sheet_title)
    assert new_wksh
    delete_worksheet(new_wksh.key, new_wksh.wksh)


def test_write_to_new_sheet(
    source_sheet_title="test_sample_tracker", new_sheet_title="test_new_sheet_write"
):
    source_df = orig_sampletracker_wksh(sheet_title=source_sheet_title).df
    new_wksh = new_worksheet_class(sheet_title=new_sheet_title)
    new_wksh.df = source_df.copy()

    response = new_wksh.write_to_sheet()

    delete_worksheet(new_wksh.key, new_wksh.wksh)

    return response


def test_delete_sheet(sheet_title="test_delete"):
    """
    Create a worksheet, delete it then check if the worksheet is in the sheets_list
    """
    new_wksh = new_worksheet_class(sheet_title=sheet_title)
    GSheet = gspread_methods.GSheet(get_test_key())
    wksh_list = GSheet.sh.worksheets()

    # delete sheet
    response = GSheet.delete_sheet(new_wksh.wksh)

    assert (
        new_wksh.sheet_title not in wksh_list
    ), f"{new_wksh.sheet_title} was not successfully deleted"


def test_new_written_sheet_eq_source():
    """
    Test for any alterations to the data that occur between reading and writing, in the absence of any user edits.

    1. instantiate a source values WorkSheet class.
    2. read source values into a second WorkSheet class.
    2. write from the second WorkSheet class into a sheet.
    3. Read the new sheet into a 3rd WorkSheet class.
    4. compare WorkSheet 1 df with WorkSheet 3 df

    """
    sheet_1_title, sheet_2_title = (
        "test_sample_tracker",
        "test_rw_df_eq_2",
    )
    # 1.
    df_1 = orig_sampletracker_wksh().df

    # 2.
    wksh_2 = new_worksheet_class(sheet_title=sheet_2_title)
    wksh_2.df = df_1.copy()
    assert wksh_2.df.equals(df_1)
    response = wksh_2.write_to_sheet()
    #    delete_worksheet(wksh_2.key, wksh_2.wksh)

    # 3.
    wksh_3 = new_worksheet_class(sheet_title=sheet_2_title)
    df_3 = wksh_3.df  # read again in a new object

    assert df_3.equals(df_1)

    delete_worksheet(wksh_3.key, wksh_3.wksh)


def main():
    test_gspread_io()


if __name__ == "__main__":
    main()
