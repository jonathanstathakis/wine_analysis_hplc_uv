from ast import alias
import duckdb as db
import pandas as pd


def write_df(con, tblname, df):
    query = f"""
        CREATE TABLE
            {tblname}
        AS SELECT
            *
        from
            df
        """

    con.sql(query)

    return None


def get_rel(con, tblname):
    query = f"""
        SELECT
            *
        FROM
            {tblname}
        """
    rel = con.sql(query).set_alias(f"{tblname}")
    return rel


df1 = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
df2 = pd.DataFrame({"col1": [1, 2, 3], "col3": ["g", "h", "i"]})

tbl1_name = "tbl1"
tbl2_name = "tbl2"
with db.connect() as con:
    write_df(con, tbl1_name, df1)
    write_df(con, tbl2_name, df2)
    tbl1 = get_rel(con, tbl1_name)
    tbl2 = get_rel(con, tbl2_name)
    join_query = f"""
        {tbl1_name}.col1={tbl2_name}.col1
        """
    joined_rel = tbl1.join(tbl2, join_query)
    result_rel = joined_rel.project("tbl1.col1, tbl1.col2, tbl2.col3").show()
