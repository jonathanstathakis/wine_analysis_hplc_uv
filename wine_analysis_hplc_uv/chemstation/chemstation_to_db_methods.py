"""
A module to contain chemstation database interface methods
"""
import json
import os
import sys

import duckdb as db
import pandas as pd
from ..db_methods import db_methods
from ..devtools import function_timer as ft


@ft.timeit
def write_chemstation_data_to_db_entry(chemstation_data_dicts_tuple, con):
    # get the intended table name
    chromatogram_spectrum_table_name = "chromatogram_spectra"
    chemstation_metadata_table_name = "chemstation_metadata"

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
            chemstation_metadata_table_name,
            chromatogram_spectrum_list,
            chromatogram_spectrum_table_name,
            con,
        )
    else:
        print(
            f"chemstation_metadata_list is dtype {type(chemstation_metadata_list)}, chromatogram_spectrum_list is dtype {type(chromatogram_spectrum_list)}. Both should be list"
        )
        print(f"{chemstation_metadata_list}")
        raise TypeError


def write_chemstation_to_db(
    chemstation_metadata_list,
    chemstation_metadata_table_name,
    chromatogram_spectrum_list,
    chromatogram_spectrum_table_name,
    con,
):
    # write metadata table, chromatogram_spectra table.
    chemstation_metadata_to_db(
        chemstation_metadata_list, chemstation_metadata_table_name, con
    )
    chromatogram_spectra_to_db(
        chromatogram_spectrum_list, chromatogram_spectrum_table_name, con
    )
    return None


def chemstation_metadata_to_db(chemstation_metadata_list, table_name, con):
    df = metadata_list_to_df(chemstation_metadata_list)
    df.pipe(check_if_table_exists_write_df_to_db, table_name, con)


def chromatogram_spectra_to_db(chromatogram_spectrum_list, table_name, con):
    df = uv_data_list_to_df(chromatogram_spectrum_list, con)
    df.pipe(check_if_table_exists_write_df_to_db, table_name, con)


def check_if_table_exists_write_df_to_db(df, table_name, con):
    """check if table currently exists:
    if does, prompt whether overwrite.
        if yes:
            drop table
            write table
        if no:
            continue.
    """
    # if yes, ask whether to overwrite. if not, ask to write.
    if table_in_db_query(table_name, con):
        if input(f"table {table_name} in {db}. overwrite? (y/n):") == "y":
            con.sql(f"DROP TABLE IF EXISTS {table_name}").execute()
            write_df_to_db(df, table_name, con)
        else:
            print(f"leaving {table_name} as is.")

    else:
        if input(f"table {table_name} not found, write to db? (y/n)") == "y":
            write_df_to_db(df, table_name, con)
        else:
            # continue without writing.
            print("test")


def table_in_db_query(table_name, con):
    query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
    result = con.sql(query).fetchone()
    return result[0] > 0


def metadata_list_to_df(uv_metadata_list):
    return pd.json_normalize(data=uv_metadata_list)


def uv_data_list_to_df(uv_data_list: list, con: db.DuckDBPyConnection) -> None:
    """ """
    spectrum_dfs = []
    for uv_data in uv_data_list:
        data = uv_data["data"]
        data["hash_key"] = uv_data["hash_key"]
        spectrum_dfs.append(data)

    combined_df = pd.concat(spectrum_dfs)
    return combined_df


def write_df_to_db(df, table_name, con):
    try:
        print(f"creating {table_name} table from df")
        con.execute(f"CREATE TABLE {table_name} AS SElECT * FROM df")
    except Exception as e:
        print(e)

    db_methods.display_table_info(con, table_name)
    return None


def main():
    return None


if __name__ == "__main__":
    main()
