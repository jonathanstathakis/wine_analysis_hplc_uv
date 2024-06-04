"""
A module for writing db queries
"""

from wine_analysis_hplc_uv.definitions import DB_PATH
import duckdb as db


def query_db(db_path: str, tbl_name: str):
    query = """--sql
    select
        vintage, name, ct_wine_name
    from
        c_sample_tracker
    ;
    """
    with db.connect(db_path) as con:
        con.sql(query).show()
    return None


def st_ct_anti_join(con):
    """
    Anti joins return the rows of the first table where a match CANNOT be found in the second.
    """
    con.sql(
        """--sql
            SELECT
            st.samplecode, st.vintage, st.name, st.ct_wine_name
            FROM
            c_sample_tracker st
            ANTI JOIN
            c_cellar_tracker ct
            ON
            st.ct_wine_name=ct.wine
            WHERE
            st.added_to_cellartracker='y'
            """
    ).show()


def ct_query(con):
    con.sql(
        """--sql
            SELECT
            *
            FROM
            c_cellar_tracker
            WHERE
            name
            LIKE
            '%tasmania%'
            """
    ).show()


def main():
    con = db.connect(DB_PATH)
    st_ct_anti_join(con)
    ct_query(con)
    return None


if __name__ == "__main__":
    # query_db(DB_PATH, CH_META_TBL_NAME)

    main()
