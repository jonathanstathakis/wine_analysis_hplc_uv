""" 
A file to contain general duckdb database methods.
"""
import os
import sys

import duckdb as db
import pandas as pd
import polars as pl
from wine_analysis_hplc_uv.chemstation import chemstation_to_db_methods
import duckdb as db
import wine_analysis_hplc_uv
from mydevtools.function_timer import timeit
import seaborn as sns
import logging

logger = logging.Logger("db")
logger.setLevel("DEBUG")
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


import pandas as pd
import duckdb as db
from wine_analysis_hplc_uv import definitions


def get_sc_df(
    con,
    sampleids: list = None,
    wavelength: list = None,
    mins: tuple = None,
    detection=list,
    type=list,
):
    """
    Form a longform spectrum chromatogram rel object for a given list of wines, wavlengths, and minutes.

    Note: mins is a tuple of 2 elements, element zero the start of the mins interval, element one is the end of the interval
    """

    # form a view from the join of sc and super and select specified columns
    join_query = f"""
             SELECT * FROM
             (
             SELECT
              sc.mins, sc.wavelength, sc.value, super.wine, super.detection, super.id
             FROM
             {definitions.CH_DATA_TBL_NAME} sc
             JOIN
             {definitions.SUPER_TBL_NAME} super
             USING (id)
             """

    # add a sample_id subset clause if sample_ids are provided
    if sampleids:
        sample_clause = f"WHERE super.id IN {tuple(sampleids)}"
        join_query += sample_clause

    # # add a wavelength subset clause if wavelengths are provided
    if wavelength:
        wavelength_clause = f"AND sc.wavelength IN {tuple(wavelength)}"
        join_query += wavelength_clause

    # # add a mins subset clause if mins are provided
    if mins:
        mins_clause = f"AND sc.mins >= {mins[0]} AND sc.mins <= {mins[1]}"
        join_query += mins_clause

    if detection:
        detection_clause = f"AND super.detection IN {tuple(detection)}"
        join_query += detection_clause

    join_query += ")"
    logger.debug(join_query)
    a = con.sql(join_query)
    return a.pl()


@timeit
def testing(con, wine_subset):
    def get_a(con_, wines_):
        return a

    a = get_a(con, wine_subset)

    return a


@timeit
def main():
    con = db.connect(wine_analysis_hplc_uv.definitions.DB_PATH)
    wines = con.sql(
        f"""
            SELECT wine from super_tbl WHERE wine NOT NULL LIMIT 167
            """
    ).fetchall()
    print(wines)

    subset_wines = tuple([wine[0] for wine in wines])
    pl_data = get_sc_df(con=con, sampleids=subset_wines)
    print(pl_data)

    @timeit
    def pl_to_df(pl_df):
        b = pl_df.to_pandas(use_pyarrow_extension_array=True)
        print(b)

    pl_to_df(pl_data)


if __name__ == "__main__":
    main()


def to_be_added_pipe():
    """
    TODO:
    - [ ] add these to a processing pipe, i.e. CT cleaner.

    A list of queries which I have directly applied to the existing super_tbl but will need to be added to a pipeline further down the track.
    """
    # clean the wine column
    con.sql(
        """UPDATE
            super_tbl
            SET
            name_ct = REPLACE(name_ct,'''','')
            """
    )
    # Add the new column
    con.sql(
        """
        ALTER TABLE super_tbl 
        ADD COLUMN wine VARCHAR;
    """
    )

    # Populate the new column
    con.sql(
        """
        UPDATE super_tbl
        SET wine = vintage_ct || ' ' || name_ct;
    """
    )
