"""
A file to contain all of the necessary cellartracker cleaning functions, to be run once the raw table is downloaded but before other operations. Works in conjuction with prototype_code/init_table_cellartracker.py
"""

import html

import duckdb as db
import numpy as np
import pandas as pd

from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods

from wine_analysis_hplc_uv.definitions import (
    TEST_DB_PATH,
    DB_PATH,
    CT_TBL_NAME,
    CLEAN_CT_TBL_NAME,
)


def clean_ct_to_db(
    in_db_path: str, in_tbl_name: str, out_tbl_name: str, out_db_path: str = None
) -> None:
    # if no out_db_path is provided, write to in_db
    if out_db_path is None:
        out_db_path = in_db_path

    dirty_df = get_tbl_as_df(db_path=in_db_path, tbl_name=in_tbl_name)

    clean_df = cellartracker_df_cleaner(df=dirty_df)

    write_clean_cellartracker_to_db(
        db_filepath=out_db_path, df=clean_df, clean_tbl_name=out_tbl_name
    )

    return None


def get_tbl_as_df(db_path: str, tbl_name: str):
    df = None
    with db.connect(db_path) as con:
        df = con.sql(f"SELECT * FROM {tbl_name}").df()
    return df


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
    print(TEST_DB_PATH)
    clean_ct_to_db(
        in_db_path=DB_PATH,
        in_tbl_name=CT_TBL_NAME,
        out_tbl_name=CLEAN_CT_TBL_NAME,
        out_db_path=TEST_DB_PATH,
    )


if __name__ == "__main__":
    main()
