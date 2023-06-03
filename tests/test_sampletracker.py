"""
Test new SampleTracker Class
"""

import os
import pandas as pd
from wine_analysis_hplc_uv.sampletracker import sampletrackerprocesser as stracker
from wine_analysis_hplc_uv.google_sheets_api import google_sheets_api


def get_columns_dict() -> dict:
    """_summary_

    Returns:
        _type_: _description_
    """
    # column names as keys, dtypes as values
    return {
        "detection": pd.StringDtype(),
        "sampler": pd.StringDtype(),
        "id": pd.StringDtype(),
        "vintage": pd.StringDtype(),
        "name": pd.StringDtype(),
        "open_date": pd.StringDtype(),
        "sampled_date": pd.StringDtype(),
        "added_to_cellartracker": pd.StringDtype(),
        "notes": pd.StringDtype(),
        "size": pd.StringDtype(),
    }


def get_google_api_dict() -> dict:
    sheet_name = "sample_tracker"
    cell_range = "!A1:Z200"

    return dict(
        spreadsheet_id="15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY",
        range=sheet_name + cell_range,
        creds_parent_path=os.environ.get("GOOGLE_SHEETS_API_CREDS_PARENT_PATH"),
    )


def strack():
    return stracker.SampleTracker(get_columns_dict(), get_google_api_dict())


def test_sampletracker_init(strack: stracker.SampleTracker = strack()):
    assert strack

    return None


def test_strack_df_is_pd(strack: stracker.SampleTracker = strack()) -> None:
    assert isinstance(strack.df, pd.DataFrame)
    return None


def test_strack_df_not_empty(strack: stracker.SampleTracker = strack()) -> None:
    assert not strack.df.empty


def test_strack_clean_df_is_pd(strack: stracker.SampleTracker = strack()) -> None:
    assert isinstance(strack.clean_df, pd.DataFrame)
    return None


def test_strack_clean_df_not_empty(strack: stracker.SampleTracker = strack()) -> None:
    assert not strack.clean_df.empty


def test_post_new_sheet(strack: stracker.SampleTracker = strack()) -> None:
    google_api_dict = get_google_api_dict()
    assert isinstance(google_api_dict, dict)
    sheet_title = "testpostcleants"
    spreadsheet_id = google_api_dict["spreadsheet_id"]
    creds_parent_path = google_api_dict["creds_parent_path"]

    google_sheets_api.delete_sheet(spreadsheet_id, sheet_title, creds_parent_path)

    new_range = sheet_title + "!A1:Z200"

    new_google_api_dict = google_api_dict
    new_google_api_dict["range"] = new_range

    strack.to_sheets(new_google_api_dict, sheet_title)

    stracker.SampleTracker(get_columns_dict(), new_google_api_dict)

    # google_sheets_api.delete_sheet(spreadsheet_id, sheet_title, creds_parent_path)

    return None


def main():
    return None


if __name__ == "__main__":
    main()
