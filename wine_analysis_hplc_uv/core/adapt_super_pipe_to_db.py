import duckdb as db
import numpy as np
import pandas as pd

from ..core.super_table_pipe import super_table_pipe
from ..db_methods import db_methods
from ..devtools import function_timer as ft
from ..devtools import project_settings
from ..ux_methods import ux_methods as ux


@ft.timeit
def load_super_table(db_filepath: str, table_1, table_2, table_3, tbl_name):
    print("###\n\nLoad Super Table\n\n###\n\n")

    ch_df, st_df, ct_df = ux.ask_user_and_execute(
        f"fetch {table_1}, {table_2}, and {table_3} tables as dfs from {db_filepath}?",
        fetch_tables,
        db_filepath=db_filepath,
        tbl_1=table_1,
        tbl_2=table_2,
        tbl_3=table_3,
    )
    assert not ch_df.empty
    assert not st_df.empty
    assert not ct_df.empty

    # with db.connect(db_filepath) as con:
    #     write_super_table_to_db(super_table_df, db_filepath, tbl_name)
    return None


def fetch_tables(db_filepath: str, tbl_1: str, tbl_2: str, tbl_3: str) -> tuple:
    with db.connect(db_filepath) as con:
        write_super_table_to_db(super_table_df, db_filepath, tbl_name)
    return None


def write_super_table_to_db(df: pd.DataFrame, db_filepath: str, tbl_name) -> None:
    with db.connect(db_filepath) as con:
        con.sql(f"CREATE TABLE {tbl_name} AS SELECT * FROM df")

    db_methods.display_table_info(db_filepath, tbl_name)


def main():
    load_super_table()


if __name__ == "__main__":
    main()
