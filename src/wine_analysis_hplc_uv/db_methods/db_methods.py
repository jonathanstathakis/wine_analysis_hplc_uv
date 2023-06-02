""" 
A file to contain general duckdb database methods.
"""
import os
import sys

import duckdb as db
import pandas as pd

from wine_analysis_hplc_uv.chemstation import chemstation_to_db_methods


from typing import List

def table_as_df(db_filepath: str, tblname:str, cols: List[str]=['*']) -> pd.DataFrame:
    """
    Get a duckdb table as a dataframe    
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
    return df

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


def write_df_to_table(
    df: pd.DataFrame,
    db_filepath: str,
    table_name: str,
    schema: str,
    table_column_names: str,
    df_column_names: str,
) -> None:
    print(f"{__file__}\n")
    print(f"writing {table_name} to {db_filepath}..\n")
    try:
        with db.connect(db_filepath) as con:
            con.sql(
                f"""
            DROP TABLE IF EXISTS {table_name};
            CREATE TABLE {table_name} ({schema});
            """
            )
    except Exception as e:
        print(
            f"Exception encountered while trying to create new table {table_name}:{e}"
        )

    insert_query = f"""
            INSERT INTO {table_name} (
            {table_column_names}
            )
            SELECT
            {df_column_names}
            FROM df;
            """
    try:
        print(f"writing to {table_name} in {db_filepath}")
        with db.connect(db_filepath) as con:
            con.sql(insert_query)
    except Exception as e:
        print(e)
        print(f"full query is:\n\n{insert_query}")
        sys.exit()
    return None

def sc_to_df(df: pd.DataFrame, db_filepath: str) -> pd.DataFrame:
    """
    Pass a wine metadata dataframe with relevant hash_key to join to spectrums contained in spectrum table found through the con object. returns the metadata df with a spectrum column, where spectrums are nested dataframes.
    """
    def get_spectra(con: db.DuckDBPyConnection, hash_key: str) -> pd.DataFrame:
        query = f"""
            SELECT * EXCLUDE (hash_key) from spectrums
            where hash_key = '{hash_key}'
            """
        df = con.sql(query).df()
        return df
    
    with db.connect(db_filepath) as con:
        df["spectra"] = df.apply(lambda row: get_spectra(con, row["hash_key"]), axis=1)

    df = df.drop("hash_key", axis=1)

    return df


def append_df_to_db_table_handler(
    df: pd.DataFrame, db_filepath: str, db_table_name: str
) -> None:
    """
    A function to append an df to an already existing db table.
    """

    def append_df(df: pd.DataFrame, db_filepath: str, db_table_name: str) -> None:
        with db.connect(db_filepath) as con:
            con.register("temp_table", df)
            con.execute(f"INSERT INTO {db_table_name} SELECT * FROM temp_table")
            con.unregister("temp_table")

    def check_if_df_added_to_table(
        df: pd.DataFrame, db_filepath: str, db_table_name: str
    ) -> bool:
        with db.connect(db_filepath) as con:
            db_new_id_df = con.execute(f"SELECT hash_key from {db_table_name}").df()
            assert not df["hash_key"].isin(db_new_id_df["hash_key"]).empty

    assert os.path.isfile(db_filepath), f"database not found at {db_filepath}."

    if not test_db_table_exists(db_filepath, db_table_name):
        chemstation_to_db_methods.create_db_table_from_df(
            df, db_table_name, db_filepath
        )
    else:
        # check if the db exists.
        # check if table exists
        test_db_table_exists(db_filepath, db_table_name)
        append_df(df, db_filepath, db_table_name)
    check_if_df_added_to_table(df, db_filepath, db_table_name)
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
