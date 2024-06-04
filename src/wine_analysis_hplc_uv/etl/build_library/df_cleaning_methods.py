"""
A file to contain a number of general pandas dataframe cleaning methods.
"""

import pandas as pd


def df_string_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    assert isinstance(df, pd.DataFrame)

    # stripping and lowering case of all string values in df
    def lowercase_and_strip(value):
        if isinstance(value, str):
            return value.lower().strip()
        return value

    df = df.applymap(lowercase_and_strip)

    # stripping and lowering case of all column and index values in df.
    # 2023-06-14 12:15:44 this has the unfortunate side effect of casting all
    # integer index vals to object. Add a test for numeric?

    def process_index(df):
        str_idx = df.index.astype(str)
        if not str_idx.str.isnumeric().all():
            df = df.rename(index=str_idx.str.strip().str.lower())
        return df

    df = df.pipe(process_index)
    # str_cols = df.columns.astype(str)

    # if not str_cols.str.isnumeric().all():
    #     df.columns = str_cols.str.strip().str.lower()

    # str_idx = df.index.astype(str)
    # if not str_idx.str.isnumeric().all():
    #     df = df.rename(index=str_idx.str.strip().str.lower())

    return df
