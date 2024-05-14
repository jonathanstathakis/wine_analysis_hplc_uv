import pandas as pd
from fuzzywuzzy import fuzz, process
import logging

logger = logging.getLogger(__name__)


def cellar_tracker_fuzzy_join(
    in_df: pd.DataFrame, cellartracker_df: pd.DataFrame
) -> pd.DataFrame:
    merge_df = _fuzzy_join(st_df=in_df, ct_df=cellartracker_df)

    assert not merge_df.empty, "merge_df formed after fuzzy join is empty"

    logger.info("df of dims %s formed after merge", merge_df.shape)
    logger.info(merge_df.head(1))

    return merge_df


def _fuzzy_join(st_df: pd.DataFrame, ct_df: pd.DataFrame) -> pd.DataFrame:
    """ """

    assert not st_df.empty
    assert not ct_df.empty

    logger.info("joining sample tracker and cellar tracker tables..")

    # create a join key as the concatenation of wine vintage and name
    st_df_with_join_key, ct_df_with_join_key = _add_join_key_column(st_df, ct_df)

    merge_df = _join_dfs_with_fuzzy(df1=st_df_with_join_key, df2=ct_df_with_join_key)

    return merge_df


def _add_join_key_column(
    st_df: pd.DataFrame,
    ct_df: pd.DataFrame,
    vintage: str = "vintage",
    wine_name: str = "name",
    join_key_name: str = "join_key",
):
    """
    To both input dfs, add a join key column `join_key_name` as the concatenation of `vintage` and
    `wine_name` columns.
    """
    input_dfs = [st_df, ct_df]
    output_dfs = []

    for df in input_dfs:
        out_df = df.copy()
        out_df[join_key_name] = out_df[vintage] + " " + out_df[wine_name]
        output_dfs.append(out_df)

    return tuple(output_dfs)


def _join_dfs_with_fuzzy(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    match_threshold_score: int = 65,
    join_key: str = "join_key",
) -> pd.DataFrame:
    """
    Use `fuzzywuzzy` to pattern match wines between cellar tracker and sample tracker

    TODO: fix all of this. Good lord.
    """

    # input validation.

    ## cast the key columns to object dtype #TODO: change to pandas string dtype
    df1, df2 = _input_preparation(df1=df1, df2=df2, join_key=join_key)

    try:
        # produces a tuple of: ('matched_string', 'match score', 'matched_string_indice').
        # Usually it's two return values, but using scorer=fuzzy.token_sort_ratio or scorer=fuzz.token_set_ratio returns the index as well.

        df1["join_key_match"] = df1[join_key].apply(
            lambda x: process.extractOne(x, df2[join_key], scorer=fuzz.token_set_ratio)
        )

    except Exception as e:
        e.add_note(str(df1[join_key].dtype))
        e.add_note(str(df2[join_key].dtype))
        raise e

    # each row of 'join_key_match' contains a two element tuple of that rows matched string (index 0) and the match score (index 1)
    # here we filter matches based on whether the score is greater than 65. if less, replace the match with None for later handling.

    df1["join_key_matched"] = df1["join_key_match"].apply(
        lambda x: x[0] if x[1] > match_threshold_score else None
    )

    # furthermore we unpack the tupled match scores into their own column "join_key_similarity"
    df1["join_key_similarity"] = df1["join_key_match"].apply(
        lambda x: x[1] if x[1] > match_threshold_score else None
    )

    # finally we remove the tuple column

    df1.drop(columns=["join_key_match"], inplace=True)

    # 'ms' indicates column was sourced from metadata-sampletracker table, 'ct' from cellartracker table.

    try:
        merge_df = pd.merge(
            df1,
            df2,
            left_on="join_key_matched",
            right_on="join_key",
            how="left",
            suffixes=["_st", "_ct"],
        )
        assert not merge_df.empty

    except AssertionError as e:
        e.add_note(
            f"""
        merge_df empty\n\ndf1
        {df1["join_key_matched"]}\n
        {df2["join_key"]}\n
        """
        )

    return merge_df


def _input_preparation(df1: pd.DataFrame, df2: pd.DataFrame, join_key: str):
    """
    Prepare the input frames for fuzzywuzzy pattern matching by casting the 'join_key'
    column to 'object' datatype and replacing any NaN with '0'
    """
    input_dfs = [df1, df2]
    output_dfs = []

    for df in input_dfs:
        try:
            out_df = df.copy()
            out_df[join_key] = df[join_key].astype(object).fillna("0")
            assert out_df[join_key].dtype == "object"
            output_dfs.append(out_df)

        except Exception as e:
            raise e

    return tuple(output_dfs)
