"""
Inner join of two tables
"""
from mydevtools import project_settings, function_timer as ft
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

        query_2 = f"""--sql
        vintage || name as join_key;
        """

        con.sql(query_1)
        con.sql(query_2)


def inner_join(db_path: str, tbl1: str, tbl2: str, tbl1_key: str, tbl2_key: str):
    return None


def main():
    inner_join(
        db_path=definitions.DB_PATH,
        tbl1=definitions.CLEAN_ST_TBL_NAME,
        tbl2=definitions.CLEAN_CT_TBL_NAME,
        tbl1_key="join_key",
        tbl2_key="join_key",
    )

    return None


if __name__ == "__main__":
    main()
