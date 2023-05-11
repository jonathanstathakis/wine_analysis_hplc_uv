import sys
import os

sys.path.append("../../")
import google_sheets_api


def sample_tracker_df_builder():
    df = google_sheets_api.get_sheets_values_as_df(
        spreadsheet_id="15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY",
        range="sample_tracker!A1:H200",
        creds_parent_path=os.environ.get("GOOGLE_SHEETS_API_CREDS_PARENT_PATH"),
    )

    df = df.dtype(
        {
            "id": "object",
            "vintage": "object",
            "name": "object",
            "open_date": "datetime64[ns]",
            "sampled_date": "datetime64[ns]",
            "notes": "object",
        }
    )
    return df


def main():
    df = sample_tracker_df_builder()
    print(df.head())
    print(df.dtypes)


if __name__ == "__main__":
    main()
