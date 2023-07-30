"""
A module for writing db queries
"""
from wine_analysis_hplc_uv.definitions import DB_PATH, CH_META_TBL_NAME
import duckdb as db


def query_db(db_path: str, tbl_name: str):
    query = """--sql
    select
        notes
    from
        c_sample_tracker
    ;
    """
    with db.connect(db_path) as con:
        a = con.sql(query).df()
        print(a[a["notes"] == ""])
    return None


def main():
    return None


if __name__ == "__main__":
    query_db(DB_PATH, CH_META_TBL_NAME)
    main()
