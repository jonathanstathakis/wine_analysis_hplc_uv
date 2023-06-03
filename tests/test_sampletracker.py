"""
Test new SampleTracker Class
"""

import os
import pandas as pd
from wine_analysis_hplc_uv.sampletracker import sampletrackerprocesser as stracker


def test_sampletracker_init():
    assert stracker.SampleTracker(get_columns_dict(), get_google_api_dict())

    return None


def get_columns_dict() -> dict:
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


def main():
    return None


if __name__ == "__main__":
    main()
