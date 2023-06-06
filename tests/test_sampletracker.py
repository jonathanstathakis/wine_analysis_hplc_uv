"""
Test new SampleTracker Class
"""

import os
import pandas as pd
from wine_analysis_hplc_uv.sampletracker import sample_tracker_processor as stracker
from wine_analysis_hplc_uv.google_sheets_api import google_sheets_api
import pytest


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
    }


@pytest.fixture(scope="module")
def google_api_dict() -> dict:
    sheet_name = "sample_tracker"
    cell_range = "!A1:Z400"

    return dict(
        spreadsheet_id="15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY",
        range=sheet_name + cell_range,
        creds_parent_path=os.environ.get("GOOGLE_SHEETS_API_CREDS_PARENT_PATH"),
    )


@pytest.fixture(scope="module")
def new_google_api_dict(google_api_dict) -> dict:
    new_google_api_dict = google_api_dict

    new_sheet_title = "testst"
    new_range = new_sheet_title + "!A1:Z400"

    new_google_api_dict["range"] = new_range

    return new_google_api_dict


@pytest.fixture(scope="module")
def strack_class(google_api_dict):
    return stracker.SampleTracker(google_api_dict=google_api_dict)


def test_sampletracker_init(strack_class):
    assert isinstance(strack_class, stracker.SampleTracker)

    return None


def test_strack_df_is_pd(strack_class) -> None:
    assert isinstance(strack_class.df, pd.DataFrame)
    return None


def test_strack_df_not_empty(strack_class) -> None:
    assert not strack_class.df.empty


def test_strack_clean_df_is_pd(strack_class) -> None:
    assert isinstance(strack_class.clean_df, pd.DataFrame)
    return None


def test_strack_clean_df_not_empty(strack_class) -> None:
    assert not strack_class.clean_df.empty


def test_data_to_post_matches_source_sheet(strack_class, google_api_dict, sheet_title):
    google_api_dict = google_api_dict

    def get_posted_data_df(
        strack_class: stracker.SampleTracker, google_api_dict: dict, sheet_title: str
    ) -> pd.DataFrame:
        response, data = strack_class.to_sheets(
            new_google_api_dict, sheet_title, clean_df=False
        )

        posted_data_df = pd.DataFrame(data[1:], columns=data[0])
        return posted_data_df

    new_range = sheet_title + "!A1:Z400"

    new_google_api_dict = google_api_dict
    new_google_api_dict["range"] = new_range

    posted_data_df = get_posted_data_df(
        strack_class=strack_class,
        google_api_dict=google_api_dict,
        sheet_title=sheet_title,
    )

    assert posted_data_df.equals(strack_class.df)

    posted_data_df = posted_data_df.astype(str)
    strack_class.df = strack_class.df.astype(str)

    return None


def test_post_raw_sheet(strack_class, google_api_dict, new_google_api_dict) -> None:
    sheet_title = "testpostcleants"
    google_api_dict = google_api_dict
    assert isinstance(google_api_dict, dict)

    def delete_sheet(google_api_dict: dict, sheet_title: str):
        spreadsheet_id = google_api_dict["spreadsheet_id"]
        creds_parent_path = google_api_dict["creds_parent_path"]

        google_sheets_api.delete_sheet(spreadsheet_id, sheet_title, creds_parent_path)

    # clean up previously written sheet, prepare for test
    delete_sheet(google_api_dict, sheet_title)

    new_strack = stracker.SampleTracker(new_google_api_dict)
    new_raw_df = new_strack.df

    original_raw_df = strack_class.df

    # 2023-06-04 00:33:00 some part of the to_sheet, from sheet process drops leading zeroes
    # so it needs to be filled back to a width of 2 to match the raw sampletracker sheet contents
    new_raw_df["id"] = new_raw_df["id"].str.zfill(2)

    assert original_raw_df.shape == new_raw_df.shape

    from wine_analysis_hplc_uv.df_methods import df_cleaning_methods as df_clean

    original_raw_df = df_clean.df_string_cleaner(original_raw_df)
    new_raw_df = df_clean.df_string_cleaner(new_raw_df)

    print("-- original_raw_df --\n")
    print(original_raw_df.head())
    print("-- new_raw_df --\n")
    print(new_raw_df.head())

    diff_df = original_raw_df.compare(new_raw_df)

    def drop_multiindex_na(df):
        cols = [(c0, c1) for (c0, c1) in df.columns if c0 in [1, 2]]
        print(cols)
        df_multi_dropna = df.dropna(axis=0, how="all", subset=cols)
        return df_multi_dropna

    drop_multiindex_na(diff_df)

    print("-- diff_df shape--\n")
    print(diff_df.shape)

    print("-- diff_df isna shape--\n")
    print(diff_df.isna().shape)

    print("-- diff_df_dtypes --\n")

    print("zip cols")
    col_list = original_raw_df.columns.tolist()
    datatype_list = [pd.StringDtype] * len(col_list)
    zip_dict = dict(zip(col_list, datatype_list))
    print(zip_dict)

    print(original_raw_df.dtypes)
    print(new_raw_df.dtypes)
    print(original_raw_df.dtypes.compare(new_raw_df.dtypes))

    no_differences = diff_df.isna().all().all()

    assert no_differences

    assert original_raw_df.equals(new_raw_df)

    # google_sheets_api.delete_sheet(spreadsheet_id, sheet_title, creds_parent_path)

    return None


# def test_post_clean_sheet(strack: stracker.SampleTracker = strack_class()) -> None:
#     google_api_dict = get_google_api_dict()
#     assert isinstance(google_api_dict, dict)
#     sheet_title = "testpostcleants"
#     spreadsheet_id = google_api_dict["spreadsheet_id"]
#     creds_parent_path = google_api_dict["creds_parent_path"]

#     google_sheets_api.delete_sheet(spreadsheet_id, sheet_title, creds_parent_path)

#     new_range = sheet_title + "!A1:Z400"

#     new_google_api_dict = google_api_dict
#     new_google_api_dict["range"] = new_range

#     strack.to_sheets(new_google_api_dict, sheet_title, clean_df=True)

#     new_strack = stracker.SampleTracker(get_columns_dict(), new_google_api_dict)
#     new_df = new_strack.clean_df

#     clean_df = strack.clean_df

#     # 2023-06-04 00:33:00 some part of the to_sheet, from sheet process drops leading zeroes
#     # so it needs to be filled back to a width of 2 to match the raw sampletracker sheet contents
#     new_df["id"] = new_df["id"].str.zfill(2)

#     from pprint import pprint

#     pprint(clean_df.equals(new_df))

#     google_sheets_api.delete_sheet(spreadsheet_id, sheet_title, creds_parent_path)

#     return None


def main():
    return None


if __name__ == "__main__":
    main()
