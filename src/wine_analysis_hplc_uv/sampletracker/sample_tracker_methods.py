import os
import sys
import pandas as pd
from wine_analysis_hplc_uv.google_sheets_api import google_sheets_api
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods


def sample_tracker_df_builder():
    df = google_sheets_api.get_sheets_values_as_df(
        spreadsheet_id="15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY",
        range="sample_tracker!A1:Z200",
        creds_parent_path=os.environ.get("GOOGLE_SHEETS_API_CREDS_PARENT_PATH"),
    )
    print(df.columns)
    assert "notes" in df.columns

    df = df[
        [
            "detection",
            "sampler",
            "id",
            "vintage",
            "name",
            "open_date",
            "sampled_date",
            "added_to_cellartracker",
            "notes",
            "size",
        ]
    ]
    df = df.astype(
        {
            "sampler": pd.StringDtype(),
            "detection": pd.StringDtype(),
            "id": pd.StringDtype(),
            "vintage": pd.StringDtype(),
            "name": pd.StringDtype(),
            "open_date": pd.StringDtype(),
            "sampled_date": pd.StringDtype()    ,
            "added_to_cellartracker": pd.StringDtype(),
            "notes": pd.StringDtype(),
            "size": pd.StringDtype(),
        }
    )

    return df


def main():
    df = sample_tracker_df_builder()
    print(df.head())
    print(df.dtypes)


if __name__ == "__main__":
    main()
