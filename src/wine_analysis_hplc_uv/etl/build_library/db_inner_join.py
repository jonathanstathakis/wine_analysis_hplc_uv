"""
Inner join of two tables
"""

from wine_analysis_hplc_uv import definitions
import duckdb as db


def form_join_key(
    db_path: str, tbl_name: str, vntg_col: str, name_col: str, join_key_cl: str
):
    """
    db_path: filepath to .db file
    tbl_name: name of db table
    vntg_col: name of vintage column
    name_col: name of wine name column
    join_key_col: mame of the newly formed join_key col
    """
    with db.connect(db_path) as con:
        query_1 = f"""--sql
        ALTER TABLE {tbl_name}
        ADD COLUMN join_key VARCHAR;
        """

        query_2 = """--sql
        vintage || name as join_key;
        """

        con.sql(query_1)
        con.sql(query_2)


def inner_join(db_path: str, tbl1: str, tbl2: str, tbl1_key: str, tbl2_key: str):
    return None


def main():
    inner_join(
        db_path=definitions.DB_PATH,
        tbl1=definitions.Clean_tbls.ST,
        tbl2=definitions.Clean_tbls.CT,
        tbl1_key="join_key",
        tbl2_key="join_key",
    )

    return None


if __name__ == "__main__":
    main()
