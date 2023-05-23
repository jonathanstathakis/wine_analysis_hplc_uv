import html

import duckdb as db
import numpy as np
import pandas as pd

from ..db_methods import db_methods
from ..df_methods import df_cleaning_methods

"""
A file to contain all of the necessary cellartracker cleaning functions, to be run once the raw table is downloaded but before other operations. Works in conjuction with prototype_code/init_table_cellartracker.py
"""


def init_cleaned_cellartracker_table(
    db_filepath: str, raw_table_name: str, cleaned_tbl_name: str
) -> None:
    raw_df = pd.DataFrame()
    with db.connect(db_filepath) as con:
        raw_df = con.sql(f"SELECT * FROM {raw_table_name}").df()

    clean_cellartracker_df = cellartracker_df_cleaner(raw_df)

    write_clean_cellartracker_to_db(db_filepath, 
                                    clean_cellartracker_df,
                                    cleaned_tbl_name
    )
    return None


def cellartracker_df_cleaner(df):
    df = df_cleaning_methods.df_string_cleaner(df)
    df.columns = df.columns.str.lower()
    df = df.rename({"wine": "name"}, axis=1)
    df = df.replace({"1001": np.nan})

    def unescape_html(s):
        return html.unescape(s)

    try:
        df["name"] = df["name"].apply(unescape_html)
    except TypeError as e:
        print("Type error encountered when cleaning html characters:", e)

    return df


def write_clean_cellartracker_to_db(
    db_filepath: str, df: pd.DataFrame, clean_tbl_name: str
) -> None:
    schema = """
    size VARCHAR,
    vintage INTEGER,
    name VARCHAR,
    locale VARCHAR,
    country VARCHAR,
    region VARCHAR,
    subregion VARCHAR,
    appellation VARCHAR,
    producer VARCHAR,
    locale VARCHAR,
    country VARCHAR,
    type VARCHAR,
    color VARCHAR,
    category VARCHAR,
    varietal VARCHAR
    """

    tbl_colnames = schema.replace(" VARCHAR", "").replace(" INTEGER", "")
    df_colnames = tbl_colnames

    db_methods.write_df_to_table(
        df, db_filepath, clean_tbl_name, schema, tbl_colnames, df_colnames
    )

    db_methods.display_table_info(db_filepath, clean_tbl_name)

    return None


def main():
    cellartracker_df_cleaner()


if __name__ == "__main__":
    main()
