f"""
Test to develop a db con wrapper

To develop a wrapper we need to test whether it can provide a connection to the db. [duckdb](ttps://duckdb.org/docs/connect.html) `.connect` automatically creates a db file at the given path if none exists so creating the wrapper should be straight forward.
"""
import pandas as pd
import pytest
import functools
import os
import logging
import duckdb as db

# import db_conftest


def db_connector(func):
    def with_connection_(*args, **kwargs):
        conn_str = conn_str
        con = db.connect(conn_str)
        try:
            rv = func(con, *args, **kwargs)
        except Exception:
            con.rollback()
            logging.error("db connection error")
            raise
        else:
            con.commit()
        finally:
            con.close()
        return rv

    return with_connection_


@pytest.fixture(scope="module")
def get_df():
    return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})


@db_connector
def df_to_tbl(con, df, arg2=None):
    df = get_df
    cur = con.cursor()
    query = """--sql
    CREATE TABLE test_tbl select * from df;
    """
    cur.sql(query)
    return df


def test_db_connector(get_df):
    df = get_df
    df_to_tbl(df=df)
