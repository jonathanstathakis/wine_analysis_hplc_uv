"""
A module to db_filepathtain chemstation database interface methods
"""
from typing import Tuple

import duckdb as db
import pandas as pd

from ..db_methods import db_methods
from ..devtools import function_timer as ft


@ft.timeit
def write_chemstation_data_to_db_entry(
    chemstation_data_dicts_tuple: Tuple[dict, dict], db_filepath: str
) -> None:
    # get the intended table name
    chromatogram_spectrum_tblname = "chromatogram_spectra"
    chemstation_metadata_tblname = "chemstation_metadata"

    # extract the lists from the list object
    chemstation_metadata_list, chromatogram_spectrum_list = (
        chemstation_data_dicts_tuple[0],
        chemstation_data_dicts_tuple[1],
    )

    if isinstance(chemstation_metadata_list, tuple) & isinstance(
        chromatogram_spectrum_list, tuple
    ):
        write_chemstation_to_db(
            chemstation_metadata_list,
            chemstation_metadata_tblname,
            chromatogram_spectrum_list,
            chromatogram_spectrum_tblname,
            db_filepath,
        )
    else:
        print(
            f"chemstation_metadata_list is dtype {type(chemstation_metadata_list)}, chromatogram_spectrum_list is dtype {type(chromatogram_spectrum_list)}. Both should be list"
        )
        print(f"{chemstation_metadata_list}")
        raise TypeError


def write_chemstation_to_db(
    chemstation_metadata_list: list,
    chemstation_metadata_tblname: str,
    chromatogram_spectrum_list: list,
    chromatogram_spectrum_tblname: str,
    db_filepath: str,
):
    # write metadata table, chromatogram_spectra table.
    chemstation_metadata_to_db(
        chemstation_metadata_list, chemstation_metadata_tblname, db_filepath
    )
    chromatogram_spectra_to_db(
        chromatogram_spectrum_list, chromatogram_spectrum_tblname, db_filepath
    )
    return None


def chemstation_metadata_to_db(
    chemstation_metadata_list: list, tblname: str, db_filepath: str
):
    df = metadata_list_to_df(chemstation_metadata_list)
    df.pipe(check_if_table_exists_write_df_to_db, tblname, db_filepath)
    return None


def chromatogram_spectra_to_db(
    chromatogram_spectrum_list: list, tblname: str, db_filepath: str
) -> None:
    df = uv_data_list_to_df(chromatogram_spectrum_list, db_filepath)
    df.pipe(check_if_table_exists_write_df_to_db, tblname, db_filepath)
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
            db_filepathtinue.
    """
    # if yes, ask whether to overwrite. if not, ask to write.
    if table_in_db_query(tblname, db_filepath):
        if input(f"table {tblname} in {db}. overwrite? (y/n):") == "y":
            with db.connect(db_filepath) as con:
                db_filepath.sql(f"DROP TABLE IF EXISTS {tblname}").execute()
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
        f"SELECT COUNT(*) FROM information_schema.tables WHERE tblname = '{tblname}'"
    )
    with db.connect(db_filepath) as con:
        result = con.sql(query).fetchone()
    return result[0] > 0


def metadata_list_to_df(uv_metadata_list: list) -> pd.DataFrame:
    return pd.json_normalize(data=uv_metadata_list)


def uv_data_list_to_df(uv_data_list: list, db_filepath: str) -> None:
    """ """
    spectrum_dfs = []
    for uv_data in uv_data_list:
        data = uv_data["data"]
        data["hash_key"] = uv_data["hash_key"]
        spectrum_dfs.append(data)

    combined_df = pd.db_filepathcat(spectrum_dfs)
    return combined_df


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
