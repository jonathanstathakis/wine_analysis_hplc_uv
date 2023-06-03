"""
Test new SampleTracker Class
"""

import os
import pandas as pd
from wine_analysis_hplc_uv.sampletracker import sampletrackerprocesser as stracker


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
    return dict(
        spreadsheet_id="15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY",
        range="sample_tracker!A1:Z200",
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


    google_api_dict = get_google_api_dict()
    assert isinstance(google_api_dict, dict)
    sheet_title = "testpostcleants"
    spreadsheet_id = google_api_dict["spreadsheet_id"]
    creds_parent_path = google_api_dict["creds_parent_path"]

    google_sheets_api.delete_sheet(spreadsheet_id, sheet_title, creds_parent_path)
    
    new_range = sheet_title + "!A1:Z200"
def main():
    return None


if __name__ == "__main__":
    main()
