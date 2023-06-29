""" 
A file to contain general duckdb database methods.
"""
import os
import sys

import duckdb as db
import pandas as pd

from wine_analysis_hplc_uv.chemstation import chemstation_to_db_methods


from typing import List


def tbl_to_df(db_filepath: str, tblname: str, cols: str = "*") -> pd.DataFrame:
    """
    Get a duckdb table as a dataframe. Provide an optinal string of column names seperated by commas, i.e. : "col1, col2, col3", defaults to * for all columns.

    if only 1 column is provided, returns a Series rather than a df.
    """

    df = pd.DataFrame()
    print(f"connecting to {db_filepath}..\n")
    with db.connect(db_filepath) as con:
        df = con.sql(
            f"""
            SELECT
                {cols}
            FROM
                {tblname}
            """
        ).df()
    # check if df only has 1 column. If so, return just that column as a Series
    if len(df.columns) == 1:
        return df[df.columns[0]]
    return df


def df_to_tbl(df: pd.DataFrame, tblname: str, db_filepath) -> None:
    """check if table currently exists:
    if does, prompt whether overwrite.
        if yes:
            drop table
            write table
        if no:
            continue.
    """
    # if yes, ask whether to overwrite. if not, ask to write.
    if table_in_db_query(tblname, db_filepath):
        print(f"{__file__}\n")
        if input(f"table {tblname} in {db_filepath}. overwrite? (y/n):") == "y":
            with db.connect(db_filepath) as con:
                con.sql(f"DROP TABLE IF EXISTS {tblname}")
            write_df_to_db(df, tblname, db_filepath)
        else:
            print(f"leaving {tblname} as is.")

    else:
        if input(f"table {tblname} not found, write to db? (y/n)") == "y":
            write_df_to_db(df, tblname, db_filepath)
        else:
            # db_filepathtinue without writing.
            print("test")


def table_in_db_query(tblname, db_filepath):
    query = (
        f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{tblname}'"
    )
    with db.connect(db_filepath) as con:
        result = con.sql(query).fetchone()
    return result[0] > 0


def write_df_to_db(df: pd.DataFrame, tblname: str, db_filepath: str):
    try:
        print(f"creating {tblname} table from df")
        with db.connect(db_filepath) as con:
            con.execute(f"CREATE TABLE {tblname} AS SElECT * FROM df")
    except Exception as e:
        print(e)

    display_table_info(db_filepath, tblname)
    return None


def create_table(db_filepath: str, db_table_name: str, schema: str) -> None:
    # check if table already exists
    if not test_db_table_exists(db_filepath, db_table_name):
        with db.connect(db_filepath) as con:
            # create table
            response = con.execute(
                f"""
                CREATE TABLE {db_table_name} ({schema})
                """
            ).fetchall()
        print(response)


def display_table_info(db_filepath: str, table_name: str) -> None:
    print(f"\n\n###### {table_name.upper()} TABLE ######\n")

    assert isinstance(db_filepath, str)

    with db.connect(db_filepath) as con:
        con.sql(f"DESCRIBE TABLE {table_name}").show()
        con.sql(f"SELECT COUNT(*) FROM {table_name}").show()
        con.sql(f"SELECT * FROM {table_name} LIMIT 5").show()
    return None


def test_db_table_exists(db_filepath: str, db_table_name: str) -> bool:
    with db.connect(db_filepath) as con:
        tables = con.execute(
            f"""
        SELECT
            name
        FROM
            sqlite_master
        WHERE
            type = 'table'
            AND
            name = '{db_table_name}'
                """
        ).fetchall()

    if len(tables) == 1:
        return True
    else:
        f"No tables with name {db_table_name} found"
        return False
