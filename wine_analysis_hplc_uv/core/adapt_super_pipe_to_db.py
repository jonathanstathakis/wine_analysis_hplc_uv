import duckdb as db
import numpy as np
import pandas as pd

from ..core.super_table_pipe import super_table_pipe
from ..db_methods import db_methods
from ..devtools import function_timer as ft
from ..devtools import project_settings


@ft.timeit
def load_super_table(db_filepath: str, table_1, table_2, table_3, tbl_name):
    print("###\n\nLoad Super Table\n\n###\n\n")

    with db.connect(db_filepath) as con:
        con.sql("drop table if exists super_table")

        print(f"loading {table_1} into df..\n")
        chemstation_df = con.sql(f"SELECT * FROM {table_1}").df()
        print(f"loading {table_2} into df..\n")
        sample_tracker_df = con.sql(f"SELECT * FROM {table_2}").df()
        print(f"loading {table_3} into df..\n")
        cellartracker_df = con.sql(f"SELECT * FROM {table_3}").df()

    cellartracker_df.vintage = cellartracker_df.vintage.astype("Int64")

    print(cellartracker_df[cellartracker_df["vintage"] == "empty"])

    print(f"Starting with {chemstation_df.shape[0]} rows in chemstation_df..\n")
    how_chemstation_sampletracker_join = "left"
    super_table_df = super_table_pipe.super_table_pipe(
        chemstation_df,
        sample_tracker_df,
        cellartracker_df,
        how_chemstation_sampletracker_join=how_chemstation_sampletracker_join,
    )

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
