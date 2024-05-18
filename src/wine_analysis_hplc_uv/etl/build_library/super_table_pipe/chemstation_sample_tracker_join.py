"""
"""
import pandas as pd

from ...ux_methods import ux_methods as ux


def chemstation_sample_tracker_join(in_df: pd.DataFrame, st_df: pd.DataFrame, how: str):
    def join_dfs(in_df: pd.DataFrame, st_df: pd.DataFrame, how: str) -> pd.DataFrame:
        print("joining metadata table with sample_tracker..\n")

        assert not in_df.empty, "in_df is empty"
        assert not st_df.empty, "in_df is empty"

        # drop "join_samplecode" entries with characters..

        assert (
            "join_samplecode" in in_df.columns
        ), "Column 'join_samplecode' does not exist in in_df"
        assert "id" in st_df.columns, "Column 'id' does not exist in sample_tracker_df"

        print(f"joining chemstation_metadata, sample_tracker with a {how} join..\n")

        merge_df = pd.merge(
            in_df,
            st_df,
            left_on="join_samplecode",
            right_on="samplecode",
            how=how,
            validate="m:1",
        )

        print(st_df["samplecode"])
        print(in_df["join_samplecode"])

        print(
            "\ndf of dims",
            merge_df.shape,
            "formed after merge of chemstation_metadata and sample_tracker.\n If this df has more rows than the inital left_df, it is because there were duplicate matches, so the rows were duplicated.\n",
        )
        assert (
            not merge_df.empty
        ), f"the result of merging in_df and st_df is an empty df. {__name__}"

        return merge_df

    merge_df = ux.ask_user_and_execute(
        "I will now attempt to join the ch and st dfs. Proceed?",
        join_dfs,
        in_df,
        st_df,
        how,
    )

    return merge_df


def main():
    return None


if __name__ == "__main__":
    main()