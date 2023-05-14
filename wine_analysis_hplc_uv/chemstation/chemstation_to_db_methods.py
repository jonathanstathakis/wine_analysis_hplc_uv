"""
A module to contain chemstation database interface methods
"""
import duckdb as db
import pandas as pd

from ..devtools import function_timer as ft, project_settings
from ..db_methods import db_methods


def metadata_list_to_df(uv_metadata_list):
    return pd.json_normalize(data=uv_metadata_list)


def uv_data_list_to_df(uv_data_list: list) -> pd.DataFrame:
    spectrum_dfs = []
    for uv_data in uv_data_list:
        data = uv_data["data"]
        data["hash_key"] = uv_data["hash_key"]
        spectrum_dfs.append(data)

    combined_df = pd.concat(spectrum_dfs)
    return combined_df


def create_db_table_from_df(df, table_name, db_filepath):
    try:
        print(f"creating {table_name} table from df")
        with db.connect(db_filepath) as con:
            con.sql(f"CREATE TABLE {table_name} AS SElECT * FROM df")
    except Exception as e:
        print(e)

    db_methods.display_table_info(db_filepath, table_name)
    return None


def main():
    return None


if __name__ == "__main__":
    main()
