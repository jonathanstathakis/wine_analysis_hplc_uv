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
from wine_analysis_hplc_uv import definitions


def write_df_to_db(df: pd.DataFrame, tblname: str, con: db.DuckDBPyConnection):
    con.execute(f"CREATE OR REPLACE TABLE {tblname} AS SElECT * FROM df")

    # display_table_info(db_filepath, tblname)
    return None


def display_table_info(con: db.DuckDBPyConnection, table_name: str) -> None:
    print(f"\n\n###### {table_name.upper()} TABLE ######\n")

    con.sql(f"DESCRIBE TABLE {table_name}").show()
    con.sql(f"SELECT COUNT(*) FROM {table_name}").show()
    con.sql(f"SELECT * FROM {table_name} LIMIT 5").show()
    return None


def get_sc_df(
    con: db.DuckDBPyConnection,
    sampleids: list = None,
    wavelength: list = None,
    mins: tuple = None,
    detection: list = None,
    # type: list = None,
):
    """
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
            {definitions.CH_DATA_TBL_NAME} sc
            JOIN
            {definitions.CLEAN_CT_TBL_NAME} super
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
                 {definitions.CH_DATA_TBL_NAME} sc
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
