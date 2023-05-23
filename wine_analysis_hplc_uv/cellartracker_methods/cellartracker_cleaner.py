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


def write_clean_cellartracker_to_db(df, con, table_name) -> None:
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
    con.sql(f"DROP TABLE IF EXISTS {table_name};")

    con.sql(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});")

    con.sql(
        f"""
        INSERT INTO {table_name} (
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


if __name__ == "__main__":
    main()
