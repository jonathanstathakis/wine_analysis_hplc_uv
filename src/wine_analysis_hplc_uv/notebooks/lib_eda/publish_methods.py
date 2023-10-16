import pandas as pd


def two_grouped_col_df(df):
    # a function for turning a long df into a 2 col table for publication
    # preference for left col to be longer than right col.
    left_length = len(df) // 2 + 1
    right_length = len(df) // 2 + 1

    df1 = df.iloc[:left_length]
    df2 = df.iloc[right_length:].reset_index(drop=True)

    concat_df = pd.concat([df1, df2], axis=1).fillna("")
    return concat_df


def display_summary_tbl(df):
    out_df = df.copy()
    out_df["prop"] = out_df["prop"].apply(np.round, 3)
    out_df = out_df.rename({"prop": "prop (%)"}, axis=1)
    return out_df
