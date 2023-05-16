"""

"""
from traceback import print_tb

import pandas as pd
from fuzzywuzzy import fuzz, process

from ...devtools import function_timer as ft
from ...devtools import project_settings
from . import form_join_col


def join_dfs_with_fuzzy(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    print("####\n\nDF FUZZY JOIN\n\n####\n")

    print("joining supplied dfs on 'join_key'..\n")

    def fuzzy_match(s1, s2):
        return fuzz.token_set_ratio(s1, s2)
    
    df1['join_key'] = df1['join_key'].astype(object)
    df2['join_key'] = df2['join_key'].astype(object)

    try:
        df1 = df1.fillna('0')
        df2 = df2.fillna('0')

    except Exception as e:
        print(f"tried to fill empties in both dfs but {e}\n")


    assert df1['join_key'].dtype == 'object', "expecting df1['join_key] to be object dtype"
    assert df2['join_key'].dtype == 'object', "expecting df2['join_key] to be object dtype"
    

    try:
        df1["join_key_match"] = df1["join_key"].apply(
            lambda x: process.extractOne(x, df2["join_key"], scorer=fuzzy_match))
        
    except Exception as e:
        print(df1["join_key"].dtype)
        print(df2["join_key"].dtype)
        print(e)
        raise TypeError

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
    assert_msg = f"""
    merge_df empty\n\ndf1
    {df1["join_key_matched"]}\n
    {df2["join_key"]}\n
    """
    assert merge_df.shape[0] > 0, assert_msg

    return merge_df


def cellar_tracker_fuzzy_join(
    in_df: pd.DataFrame, cellartracker_df: pd.DataFrame
) -> pd.DataFrame:
    """
    change all id edits to 'new id'. merge sample_tracker on new_id. Spectrum table will be joined on exp_id.

    in df can be anything, but for the main pipe at 2023-05-16 15:01:54 it is the joined chemstation, sampletracker table.
    """
    assert not in_df.empty, "in_df is empty\n"

    assert not cellartracker_df.empty, "cellartracker_df is empty\n"
    print("####\n\njoining metadata_table+sample_tracker with cellar_tracker\n\n####\n")
    cellartracker_df.attrs["name"] = "cellar tracker table"


    in_df = form_join_col.form_join_col(in_df)
    cellartracker_df = form_join_col.form_join_col(cellartracker_df)

    merge_df = join_dfs_with_fuzzy(in_df, cellartracker_df)

    print("df of dims", merge_df.shape, "formed after merge")
    return merge_df


def main():
    return None


if __name__ == "__main__":
    main()
