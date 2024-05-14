"""
A file to contain general duckdb database methods.
"""

import pandas as pd
from wine_analysis_hplc_uv import definitions
from mydevtools.function_timer import timeit
import logging
import duckdb as db
from deprecated import deprecated

logger = logging.getLogger(__name__)


def write_df_to_db(df: pd.DataFrame, tblname: str, con: db.DuckDBPyConnection):
    try:
        # write given table in db from df
        con.sql(f"CREATE OR REPLACE TABLE {tblname} AS SElECT * FROM df")

        db_name = con.sql("SELECT current_database()").fetchone()[0]  # type: ignore

        # log that the tbl has been written to the db
        logger.info(f"{tblname} written to {db_name}")
    except db.CatalogException as e:
        logger.error(e)
        # get list of all tables in db
        logger.error(
            "tables in db:" f" {con.sql('SELECT table_name FROM duckdb_tables()').df()}"
        )
    # double check that table is in db
    try:
        tbls_in_db = con.sql("SELECT table_name FROM duckdb_tables").df()
        assert tblname in tbls_in_db.values
    except AssertionError:
        logger.error(f"\n{tbls_in_db}")
        logger.error(msg=f"db is: {db_name}")

    # display_table_info(db_filepath, tblname)
    return None


def display_table_info(con: db.DuckDBPyConnection, table_name: str) -> None:
    print(f"\n\n###### {table_name.upper()} TABLE ######\n")

    con.sql(f"DESCRIBE TABLE {table_name}").show()
    con.sql(f"SELECT COUNT(*) FROM {table_name}").show()
    con.sql(f"SELECT * FROM {table_name} LIMIT 5").show()
    return None


@deprecated(reason="use `wine_analysis_hplc_uv.queries.GetSampleData")
def get_sc_df(
    con: db.DuckDBPyConnection,
    sampleids: list = None,
    wavelength: list = None,
    mins: tuple = None,
    detection: list = None,
    # type: list = None,
):
    """
    2023-08-01 12:42:39 Note: this is currently defunct as I want to focus on developing queries from scratch every time so i get more comfortable writing them. Keeping to provide groundwork for future user-facing functionality.

    Form a longform spectrum chromatogram rel object for a given list of wines, wavelengths, and minutes.

    Note: mins is a tuple of 2 elements, element zero the start of the mins interval, element one is the end of the interval
    """

    # form a view from the join of sc and super and select specified columns
    join_query = f"""
            SELECT * FROM
            (
            SELECT
            sc.mins, sc.wavelength, sc.value, super.wine, super.detection, super.id
            FROM
            {definitions.Raw_tbls.CH_DATA} sc
            JOIN
            {definitions.Clean_tbls.CT} super
            USING (id)
            """

    conditions = []

    if sampleids:
        conditions.append(f"super.id IN {tuple(sampleids)}")

    if wavelength:
        conditions.append(f"sc.wavelength IN {tuple(wavelength)}")

    if mins:
        conditions.append(f"sc.mins >= {mins[0]} AND sc.mins <= {mins[1]}")

    if detection:
        conditions.append(f"super.detection IN {tuple(detection)}")

    conditions_clause = " AND ".join(conditions)

    join_query = f"""
                 SELECT * FROM
                 (
                 SELECT
                  sc.mins, sc.wavelength, sc.value, super.wine, super.detection, super.id
                 FROM
                 {definitions.Raw_tbls.CH_DATA} sc
                 JOIN
                 {definitions.SUPER_TBL_NAME} super
                 USING (id)
                 """

    if conditions_clause:
        join_query += f" WHERE {conditions_clause}"
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
