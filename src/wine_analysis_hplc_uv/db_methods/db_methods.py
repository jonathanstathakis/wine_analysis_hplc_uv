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


def get_sc_df(con, wines: list = None, wavelength: list = None, mins: tuple = None):
    """
    Form a longform spectrum chromatogram rel object for a given list of wines, wavlengths, and minutes.

    Note: mins is a tuple of 2 elements, element zero the start of the mins interval, element one is the end of the interval
    """

    # get the super tbl
    super_rel = con.sql(
        "SELECT CONCAT(vintage_ct,  ' ', name_ct) AS wine, id FROM"
        f" {definitions.SUPER_TBL_NAME}"
    ).set_alias("super_rel")

    # get sc_tbl
    sc_rel = con.sql(f"SELECT * FROM {definitions.CH_DATA_TBL_NAME}").set_alias(
        "sc_rel"
    )

    # form the desired columns from the join dropping super_rel id
    # this is an arbitrary choice, they are duplicate columns
    sc_rel_cols = [f"sc_rel.{col}" for col in sc_rel.columns]
    super_rel_cols = [f"super_rel.{col}" for col in super_rel.columns if col != "id"]
    super_sc_rel_cols = sc_rel_cols + super_rel_cols

    # join them
    join_query = f"""
             SELECT {",".join(super_sc_rel_cols)}
             FROM
             sc_rel
             JOIN
             super_rel
             ON (sc_rel.id=super_rel.id)
             """
    assert not None in wines, f"{wines}"
    if wines:
        wine_clause = f"WHERE super_rel.wine IN {tuple(wines)}"
        join_query += wine_clause

    if wavelength:
        wavelength_clause = f"AND sc_rel.wavelength IN {wavelength}"
        join_query += wavelength_clause

    if mins:
        mins_clause = f"AND sc_rel.mins >= {mins[0]} AND sc_rel.mins <= {mins[1]}"
        join_query += mins_clause

    super_sc_rel = con.sql(join_query)

    # remove the table/rel prefixes from the column names in the prior list then check if the resulting tbl/df has the same columns
    assert [s.split(".")[1] for s in super_sc_rel_cols] == super_sc_rel.columns

    # check that expected wavelengths in join
    if wavelength:
        assert set(wavelength) == set(
            super_sc_rel.wavelength.df().iloc[:, 0].drop_duplicates().tolist()
        )

    # apparently rel objects expire when they pass out of scope..?
    # import polars as pl
    r = super_sc_rel
    return r.pl()


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
    pl_data = get_sc_df(con=con, wines=subset_wines)
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
