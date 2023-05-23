"""
A module to dbfilepathtain chemstation database interface methods
"""
from typing import Tuple

import duckdb as db
import pandas as pd

from ..db_methods import db_methods
from ..devtools import function_timer as ft


@ft.timeit
def write_chemstation_data_to_db_entry(
    chemstation_data_dicts_tuple: Tuple[dict, dict], dbfilepath: str
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
            dbfilepath,
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
    dbfilepath: str,
):
    # write metadata table, chromatogram_spectra table.
    chemstation_metadata_to_db(
        chemstation_metadata_list, chemstation_metadata_tblname, dbfilepath
    )
    chromatogram_spectra_to_db(
        chromatogram_spectrum_list, chromatogram_spectrum_tblname, dbfilepath
    )
    return None


def chemstation_metadata_to_db(
    chemstation_metadata_list: list, tblname: str, dbfilepath: str
):
    df = metadata_list_to_df(chemstation_metadata_list)
    df.pipe(check_if_table_exists_write_df_to_db, tblname, dbfilepath)
    return None


def chromatogram_spectra_to_db(
    chromatogram_spectrum_list: list, tblname: str, dbfilepath: str
) -> None:
    df = uv_data_list_to_df(chromatogram_spectrum_list, dbfilepath)
    df.pipe(check_if_table_exists_write_df_to_db, tblname, dbfilepath)
    return None


def check_if_table_exists_write_df_to_db(
    df: pd.DataFrame, tblname: str, dbfilepath
) -> None:
    """check if table currently exists:
    if does, prompt whether overwrite.
        if yes:
            drop table
            write table
        if no:
            dbfilepathtinue.
    """
    # if yes, ask whether to overwrite. if not, ask to write.
    if table_in_db_query(tblname, dbfilepath):
        if input(f"table {tblname} in {db}. overwrite? (y/n):") == "y":
            with db.connect(dbfilepath) as con:
                dbfilepath.sql(f"DROP TABLE IF EXISTS {tblname}").execute()
            write_df_to_db(df, tblname, dbfilepath)
        else:
            print(f"leaving {tblname} as is.")

    else:
        if input(f"table {tblname} not found, write to db? (y/n)") == "y":
            write_df_to_db(df, tblname, dbfilepath)
        else:
            # dbfilepathtinue without writing.
            print("test")


def table_in_db_query(tblname, dbfilepath):
    query = (
        f"SELECT COUNT(*) FROM information_schema.tables WHERE tblname = '{tblname}'"
    )
    with db.connect(dbfilepath) as con:
        result = con.sql(query).fetchone()
    return result[0] > 0


def metadata_list_to_df(uv_metadata_list: list) -> pd.DataFrame:
    return pd.json_normalize(data=uv_metadata_list)


def uv_data_list_to_df(uv_data_list: list, dbfilepath: str) -> None:
    """ """
    spectrum_dfs = []
    for uv_data in uv_data_list:
        data = uv_data["data"]
        data["hash_key"] = uv_data["hash_key"]
        spectrum_dfs.append(data)

    combined_df = pd.dbfilepathcat(spectrum_dfs)
    return combined_df


def write_df_to_db(df: pd.DataFrame, tblname: str, dbfilepath: str):
    try:
        print(f"creating {tblname} table from df")
        with db.connect(dbfilepath) as con:
            con.execute(f"CREATE TABLE {tblname} AS SElECT * FROM df")
    except Exception as e:
        print(e)

    db_methods.display_table_info(dbfilepath, tblname)
    return None


def main():
    return None


if __name__ == "__main__":
    main()
