import os
from typing import Dict
import pandas as pd
from wine_analysis_hplc_uv.google_sheets_api import google_sheets_api
from wine_analysis_hplc_uv.my_sheetsinterface.gspread_methods import WorkSheet


def get_gsheet_key(envar: str = "SAMPLETRACKER_KEY"):
    return os.environ.get(envar)


def sample_tracker_df_builder(
    key=get_gsheet_key(), sheet_title="sample_tracker", dtype=object
):
    df = WorkSheet(key=key, sheet_title=sheet_title)

    def make_dtype_dict(df: pd.DataFrame, dtype: type = pd.StringDtype) -> dict:
        f"converting input df dtypes to {dtype}..\n"
        col_list = df.columns.tolist()
        datatype_list = [dtype] * len(col_list)
        zip_dict = dict(zip(col_list, datatype_list))

        return zip_dict

    # from the imported range, only select the specified columns

    dtype_dict = make_dtype_dict(df, dtype)
    return_df = df.astype(dtype_dict)

    return return_df


def st_to_sheets(df: pd.DataFrame, google_api_dict: dict, sheet_title: str) -> None:
    """
    Post sampletracker to a given sheet
    """

    spreadsheet_id = google_api_dict["spreadsheet_id"]
    creds_parent_path = google_api_dict["creds_parent_path"]
    sheet_range = google_api_dict["range"]

    response = google_sheets_api.post_new_sheet(
        spreadsheet_id,
        sheet_title,
        creds_parent_path,
    )

    response, data = google_sheets_api.post_df_as_sheet_values(
        df, spreadsheet_id, sheet_range, creds_parent_path
    )
    return response, data


def main():
    df = sample_tracker_df_builder()
    print(df.head())
    print(df.dtypes)


if __name__ == "__main__":
    main()
