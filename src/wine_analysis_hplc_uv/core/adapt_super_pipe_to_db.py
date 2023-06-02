import duckdb as db
import numpy as np
import pandas as pd

from ..core.super_table_pipe import super_table_pipe
from ..db_methods import db_methods
from ..ux_methods import ux_methods as ux


@ft.timeit
def load_super_table(db_filepath: str, table_1, table_2, table_3, tbl_name):
    print("###\n\nLoad Super Table\n\n###\n\n")

    ch_df, st_df, ct_df = ux.ask_user_and_execute(
        f"from:\n\n{db_filepath}\n\nI am fetching:\n\n\t{table_1}\n\t{table_2}\n\t{table_3}\n\ntables as dfs from {db_filepath}.\n\nProceed?",
        fetch_tables,
        db_filepath=db_filepath,
        tbl_1=table_1,
        tbl_2=table_2,
        tbl_3=table_3,
    )

    assert not ch_df.empty
    assert not st_df.empty
    assert not ct_df.empty

    print(f"ch_df has shape: {ch_df.shape}")
    print(f"st_df has shape: {st_df.shape}")
    print(f"ct_df has shape: {ct_df.shape}")

    print(f"first row of ch_df:\n\n{ch_df.head(1)}")
    print(f"first row of st_df:\n\n{st_df.head(1)}")
    print(f"first row of ct_df:\n\n{ct_df.head(1)}")

    # sample_tracker_df["id"] = sample_tracker_df["id"].astype("object")

    how_chemstation_sampletracker_join = "left"
    super_table_df = ux.ask_user_and_execute(
        "Begin super table joins?",
        super_table_pipe.super_table_pipe,
        ch_df,
        st_df,
        ct_df,
        how_chemstation_sampletracker_join=how_chemstation_sampletracker_join,
    )

    ux.ask_user_and_execute(
        "write super_table to db?",
        write_super_table_to_db,
        super_table_df,
        db_filepath,
        tbl_name,
    )

    return None


def fetch_tables(db_filepath: str, tbl_1: str, tbl_2: str, tbl_3: str) -> tuple:
    with db.connect(db_filepath) as con:
        con.sql("drop table if exists super_table")

        print(f"loading {tbl_1} into df..\n", end="")
        ch_df = con.sql(f"SELECT * FROM {tbl_1}").df()
        print(f"loading {tbl_2} into df..\n", end="")
        st_df = con.sql(
            f"SELECT CAST(id as VARCHAR) AS id, vintage, name, open_date, sampled_date, notes FROM {tbl_2}"
        ).df()
        print(f"loading {tbl_3} into df..\n", end="")
        ct_df = con.sql(f"SELECT * FROM {tbl_3}").df()
        print("")
        return ch_df, st_df, ct_df


def write_super_table_to_db(df: pd.DataFrame, db_filepath: str, tbl_name) -> None:
    with db.connect(db_filepath) as con:
        con.sql(f"CREATE TABLE {tbl_name} AS SELECT * FROM df")

    db_methods.display_table_info(db_filepath, tbl_name)


def main():
    load_super_table()


if __name__ == "__main__":
    main()
