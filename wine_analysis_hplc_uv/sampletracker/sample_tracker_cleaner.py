"""
Basic clean on sample_tracker. as of 2023-04-19 doesn't need it, but good to be safe for future issues.
"""
import html
import os

import duckdb as db
import numpy as np
import pandas as pd

from ..db_methods import db_methods
from ..df_methods import df_cleaning_methods


def clean_sample_tracker_table(
    db_filepath: str,
    raw_sample_tracker_table_name: str
) -> None:
    print("generating raw_sample_tracker_table from db")

    with db.connect(db_filepath) as con:
        raw_sample_tracker_df = con.sql(
            f"SELECT * FROM {raw_sample_tracker_table_name}"
            ).df()

    cleaned_sample_tracker_df = sample_tracker_df_cleaner(
        raw_sample_tracker_df)

    new_db_table_name = raw_sample_tracker_table_name.replace("raw", "cleaned")

    write_clean_sample_tracker_to_db(
        cleaned_sample_tracker_df, db_filepath, new_db_table_name)

    return None


def sample_tracker_df_cleaner(df):
    print("cleaning raw_sample_tracker_df")
    try:
        df = df_cleaning_methods.df_cleaning_methods.df_string_cleaner(df)
        df.columns = df.columns.str.lower()
    except Exception as e:
        print(f"while cleaning raw_sample_tracker_df, encountered Exception: {e}")

    return df


def write_clean_sample_tracker_to_db(df: pd.DataFrame,
                                     db_filepath: str,
                                     table_name: str) -> None:
    schema = """
        id INTEGER,
        vintage VARCHAR,
        name VARCHAR,
        open_date DATE,
        sampled_date DATE,
        added_to_cellartracker VARCHAR,
        notes VARCHAR,
        size INTEGER
    """

    col_names = """
        id,
        vintage,
        name,
        open_date,
        sampled_date,
        added_to_cellartracker,
        notes,
        size
    """

    db_methods.write_df_to_table(
        df,
        db_filepath,
        table_name,
        schema,
        table_column_names=col_names,
        df_column_names=col_names,
    )

    return None


def main():
    return None

if __name__ == "__main__":
    main()
