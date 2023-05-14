"""
Basic clean on sample_tracker. as of 2023-04-19 doesn't need it, but good to be safe for future issues.
"""
import html

import duckdb as db
import numpy as np
import pandas as pd

from ..db_methods import db_methods
from ..df_methods import df_cleaning_methods


def init_cleaned_sample_tracker_table(
    con: db.DuckDBPyConnection, raw_table_name: str
) -> None:
    print("generating raw_sample_tracker_table from db")
    raw_sample_tracker_df = con.sql(f"SELECT * FROM {raw_table_name}").df()

    cleaned_sample_tracker_df = sample_tracker_df_cleaner(raw_sample_tracker_df)

    out_name = raw_table_name.replace("raw", "cleaned")

    write_clean_sample_tracker_to_db(cleaned_sample_tracker_df, con, out_name)

    return None


def sample_tracker_df_cleaner(df):
    print("cleaning raw_sample_tracker_df")
    try:
        df = df_cleaning_methods.df_cleaning_methods.df_string_cleaner(df)
        df.columns = df.columns.str.lower()
    except Exception as e:
        print(f"while cleaning raw_sample_tracker_df, encountered Exception: {e}")

    return df


def write_clean_sample_tracker_to_db(df, con, table_name) -> None:
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
        con,
        table_name,
        schema,
        table_column_names=col_names,
        df_column_names=col_names,
    )

    return None


def main():
    sample_tracker_df_cleaner()


if __name__ == "__main__":
    main()
