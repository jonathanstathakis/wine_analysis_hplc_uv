"""
Basic clean on sample_tracker. as of 2023-04-19 doesn't need it, but good to be safe for future issues.
"""
import html
import pandas as pd
import duckdb as db
import numpy as np

from df_cleaning_methods import df_string_cleaner
from db_methods import display_table_info, write_df_to_table

def init_cleaned_sample_tracker_table(con : db.DuckDBPyConnection, raw_table_name : str) -> None:
    
    raw_sample_tracker_df = con.sql(f"SELECT * FROM {raw_table_name}").df()
    
    cleaned_sample_tracker_df = sample_tracker_df_cleaner(raw_sample_tracker_df)
    
    out_name = raw_table_name.replace('raw','cleaned')

    write_clean_sample_tracker_to_db(cleaned_sample_tracker_df, con, out_name)

def sample_tracker_df_cleaner(df):
    try:
        df = df_string_cleaner(df)
        df.columns = df.columns.str.lower()
    except:
        print(df.dtypes)

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
    
    write_df_to_table(df, con, table_name, schema, table_column_names = col_names, df_column_names = col_names)

    display_table_info(con, table_name)

def main():
    sample_tracker_df_cleaner()

if __name__ == '__main__':
    main()