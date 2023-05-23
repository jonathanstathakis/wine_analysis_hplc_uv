import html
import pandas as pd
import duckdb as db
import numpy as np

from ..df_methods import df_cleaning_methods
from ..db_methods import db_methods

"""
A file to contain all of the necessary cellartracker cleaning functions, to be run once the raw table is downloaded but before other operations. Works in conjuction with prototype_code/init_table_cellartracker.py
"""


def init_cleaned_cellartracker_table(
    con: db.DuckDBPyConnection, raw_table_name: str
) -> None:
    raw_cellartracker_df = con.sql(f"SELECT * FROM {raw_table_name}").df()

    clean_cellartracker_df = cellartracker_df_cleaner(raw_cellartracker_df)

    out_name = raw_table_name.replace("raw", "cleaned")

    write_clean_cellartracker_to_db(clean_cellartracker_df, con, out_name)


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


    name VARCHAR,
    locale VARCHAR,
    country VARCHAR,
    schema = """
    size VARCHAR,
    vintage INTEGER,
    name VARCHAR,
    region VARCHAR,
    subregion VARCHAR,
    appellation VARCHAR,
    producer VARCHAR,
    type VARCHAR,
    color VARCHAR,
    category VARCHAR,
    varietal VARCHAR
    """
    con.sql(f"DROP TABLE IF EXISTS {table_name};")

        INSERT INTO {table_name} (
        size,
        vintage,

        locale,

        region,
        subregion,
        appellation,
        producer,
        type,
        color,
        category,
        varietal
        )
        SELECT
        size,
        vintage,
        name,
        locale,
        country,
        region,
        subregion,
        appellation,
        producer,
        type,
        color,
        category,
        varietal
        FROM df;
        """
    )

    db_methods.display_table_info(con, table_name)


def main():
    cellartracker_df_cleaner()



    main()
