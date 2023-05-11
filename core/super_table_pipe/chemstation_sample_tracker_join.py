"""
"""
from devtools import project_settings, function_timer as ft
import pandas as pd


def chemstation_sample_tracker_join(
    in_df: pd.DataFrame, sample_tracker_df: pd.DataFrame
) -> pd.DataFrame:
    print("\n########\njoining metadata table with sample_tracker\n########")

    print(f"\nin_df has shape: {in_df.shape}\n\tcolumns: {str(list(in_df.columns))}")
    print(f"\nsample_tracker_df has shape {sample_tracker_df.shape}")

    sample_tracker_df = sample_tracker_df[
        ["id", "vintage", "name", "open_date", "sampled_date", "notes"]
    ]

    sample_tracker_df["id"] = sample_tracker_df["id"].astype("object")

    merge_df = pd.merge(
        in_df, sample_tracker_df, left_on="new_id", right_on="id", how="inner"
    )

    print(
        "\ndf of dims",
        merge_df.shape,
        "formed after merge of chemstation_metadata and sample_tracker.\n If this df has more rows than the inital left_df, it is because there were duplicate matches, so the rows were duplicated.",
    )

    return merge_df


def main():
    return None


if __name__ == "__main__":
    main()
