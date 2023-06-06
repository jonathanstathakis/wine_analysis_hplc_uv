"""
A file to contain a number of general pandas dataframe cleaning methods.
"""
import pandas as pd


def df_string_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    # stripping and lowering case of all string values in df
    def lowercase_and_strip(value):
        if isinstance(value, str):
            return value.lower().strip()
        return value

    df = df.applymap(lowercase_and_strip)

    # stripping and lowering case of all column and index values in df

    df = df.columns.astype(str).str.strip().str.lower()
    df = df.index.astype(str).str.strip().str.lower()

    return df
