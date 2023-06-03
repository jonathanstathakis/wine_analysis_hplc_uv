import os
from typing import Dict
import pandas as pd
from wine_analysis_hplc_uv.google_sheets_api import google_sheets_api


def sample_tracker_df_builder(columns_dict: Dict, google_api_dict: Dict):
    df = google_sheets_api.get_sheets_values_as_df(
        spreadsheet_id=google_api_dict["spreadsheet_id"],
        range=google_api_dict["range"],
        creds_parent_path=google_api_dict["creds_parent_path"],
    )

    # from the imported range, only select the specified columns
    df = df[columns_dict.keys()]

    # set the dtype of those columns
    df = df.astype(columns_dict)

    return df


def main():
    df = sample_tracker_df_builder()
    print(df.head())
    print(df.dtypes)


if __name__ == "__main__":
    main()
