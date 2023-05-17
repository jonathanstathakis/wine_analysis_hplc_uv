"""
"""
import pandas as pd

from ...devtools import function_timer as ft, project_settings


def chemstation_sample_tracker_join(
    in_df: pd.DataFrame, sample_tracker_df: pd.DataFrame, how: str) -> pd.DataFrame:
    print("\n####\n\njoining metadata table with sample_tracker\n\n####\n")

    assert not in_df.empty, "in_df is empty"
    assert not sample_tracker_df.empty, "in_df is empty"

    # drop "new_id" entries with characters..

    assert 'new_id' in in_df.columns, "Column 'new_id' does not exist in in_df"
    assert 'id' in sample_tracker_df.columns, "Column 'id' does not exist in sample_tracker_df"

    print(f"joining chemstation_metadata, sample_tracker with a {how} join..\n")
    
    merge_df = pd.merge(
        in_df, sample_tracker_df, left_on="new_id", right_on="id", how=how, validate="m:1"
    )

    print(sample_tracker_df['id'])
    print(in_df['new_id'])

    print(
        "\ndf of dims",
        merge_df.shape,
        "formed after merge of chemstation_metadata and sample_tracker.\n If this df has more rows than the inital left_df, it is because there were duplicate matches, so the rows were duplicated.\n",
    )
    assert not merge_df.empty, 'At end of merge_df is empty'
    return merge_df


def main():
    return None


if __name__ == "__main__":
    main()
