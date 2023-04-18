import os
import sys
import duckdb as db
import pandas as pd
sys.path.append('../')

def write_table_from_df(df : pd.DataFrame, con : db.connect, table_name : str, schema : str, target_columns : str, column_assignment : str):
    """
    Delete an existing table and replace with the downloaded one.
    """

    con.sql(f"DROP TABLE {table_name}")

    con.sql(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
    {schema}
    );
    """)
    
    query_1 = f"""
    INSERT INTO {table_name} (
        {target_columns})
    SELECT 
        {column_assignment}
    FROM df
    """
    con.execute(query_1)

def table_exists_query(con, table_name : str):
    query = f"""
    SELECT
    name
    FROM sqlite_master
    WHERE
    type = 'table'
    and name='{table_name}';
    """
    return query

    con.sql(query).show()