"""
A module to db_filepathtain chemstation database interface methods
"""
from typing import Tuple, List, Dict

import duckdb as db
import pandas as pd

from wine_analysis_hplc_uv.db_methods import db_methods


def write_chemstation_to_db(
    self,
    chemstation_metadata_tblname: str,
    chromatogram_spectrum_tblname: str,
    db_filepath: str,
) -> None:
    # write metadata table, chromatogram_spectra table.

    metadata_df_to_db(
        metadata_df=self.metadata_df,
        tblname=chemstation_metadata_tblname,
        db_filepath=db_filepath,
    )
    data_df_to_db(
        data_df=self.data_df,
        tblname=chromatogram_spectrum_tblname,
        db_filepath=db_filepath,
    )
    return None


def metadata_df_to_db(metadata_df: pd.DataFrame, tblname: str, db_filepath: str):
    metadata_df.pipe(check_if_table_exists_write_df_to_db, tblname, db_filepath)
    return None


def data_df_to_db(data_df: pd.DataFrame, tblname: str, db_filepath: str) -> None:
    data_df.pipe(check_if_table_exists_write_df_to_db, tblname, db_filepath)
    return None


def check_if_table_exists_write_df_to_db(
    df: pd.DataFrame, tblname: str, db_filepath
) -> None:
    """check if table currently exists:
    if does, prompt whether overwrite.
        if yes:
            drop table
            write table
        if no:
            continue.
    """
    # if yes, ask whether to overwrite. if not, ask to write.
    if table_in_db_query(tblname, db_filepath):
        print(f"{__file__}\n")
        if input(f"table {tblname} in {db_filepath}. overwrite? (y/n):") == "y":
            with db.connect(db_filepath) as con:
                con.sql(f"DROP TABLE IF EXISTS {tblname}")
            write_df_to_db(df, tblname, db_filepath)
        else:
            print(f"leaving {tblname} as is.")

    else:
        if input(f"table {tblname} not found, write to db? (y/n)") == "y":
            write_df_to_db(df, tblname, db_filepath)
        else:
            # db_filepathtinue without writing.
            print("test")


def table_in_db_query(tblname, db_filepath):
    query = (
        f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{tblname}'"
    )
    with db.connect(db_filepath) as con:
        result = con.sql(query).fetchone()
    return result[0] > 0


def write_df_to_db(df: pd.DataFrame, tblname: str, db_filepath: str):
    try:
        print(f"creating {tblname} table from df")
        with db.connect(db_filepath) as con:
            con.execute(f"CREATE TABLE {tblname} AS SElECT * FROM df")
    except Exception as e:
        print(e)

    db_methods.display_table_info(db_filepath, tblname)
    return None


def main():
    return None


if __name__ == "__main__":
    main()
