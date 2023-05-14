"""

"""
import pandas as pd
from fuzzywuzzy import fuzz, process

from ...devtools import function_timer as ft, project_settings
from . import form_join_col


def join_dfs_with_fuzzy(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    def fuzzy_match(s1, s2):
        return fuzz.token_set_ratio(s1, s2)

    try:
        df1 = df1.fillna("empty")
        df2 = df2.fillna("empty")
    except Exception as e:
        print(f"tried to fill empties in both dfs but {e}")

    df1["join_key_match"] = df1["join_key"].apply(
        lambda x: process.extractOne(x, df2["join_key"], scorer=fuzzy_match)
    )

    # the above code produces a tuple of: ('matched_string', 'match score', 'matched_string_indice'). Usually it's two return values, but using scorer=fuzzy.token_sort_ratio or scorer=fuzz.token_set_ratio returns the index as well.

    df1["join_key_matched"] = df1["join_key_match"].apply(
        lambda x: x[0] if x[1] > 65 else None
    )
    df1["join_key_similarity"] = df1["join_key_match"].apply(
        lambda x: x[1] if x[1] > 65 else None
    )

    df1.drop(columns=["join_key_match"], inplace=True)

    # 'ms' indicates column was sourced from metadata-sampletracker table, 'ct' from cellartracker table.
    merge_df = pd.merge(
        df1,
        df2,
        left_on="join_key_matched",
        right_on="join_key",
        how="left",
        suffixes=["_ms", "_ct"],
    )

    return merge_df


def cellar_tracker_fuzzy_join(
    in_df: pd.DataFrame, cellartracker_df: pd.DataFrame
) -> pd.DataFrame:
    """
    change all id edits to 'new id'. merge sample_tracker on new_id. Spectrum table will be merged on exp_id.
    """
    print("joining metadata_table+sample_tracker with cellar_tracker metadata")
    cellartracker_df.attrs["name"] = "cellar tracker table"

    in_df, cellartracker_df = form_join_col.form_join_col(
        in_df
    ), form_join_col.form_join_col(cellartracker_df)

    merge_df = join_dfs_with_fuzzy(in_df, cellartracker_df)

    print("df of dims", merge_df.shape, "formed after merge")
    return merge_df


def main():
    return None


if __name__ == "__main__":
    main()
