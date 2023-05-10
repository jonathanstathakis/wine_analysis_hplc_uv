"""
A module to contain chemstation database interface methods
"""
from prototype_code import db_methods
import os
import sys
from prototype_code import function_timer  as ft
import pandas as pd
import duckdb as db

@ft.timeit
def write_ch_metadata_table_to_db(uv_metadata, con):

    table_name = 'raw_chemstation_metadata'
    con.sql(f"DROP TABLE IF EXISTS {table_name}")
    
    df = pd.json_normalize(data = uv_metadata)
    
    try:
        print(f'creating {table_name} table from df')
        con.execute(f"CREATE TABLE {table_name} AS SElECT * FROM df")
    except Exception as e:
        print(e)
    
    db_methods.display_table_info(con, table_name)
    
    return None

def write_spectrum_table_to_db(uv_data_list : list, con : db.DuckDBPyConnection) -> None:

    table_name = 'spectrums'
    con.sql(f"DROP TABLE IF EXISTS {table_name}")

    spectrum_dfs = []
    for uv_data in uv_data_list:
        data = uv_data['data']
        data['hash_key'] = uv_data['hash_key']
        spectrum_dfs.append(data)

    combined_df = pd.concat(spectrum_dfs)

    try:
        print(f'creating {table_name} table from combined_df')
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM combined_df")
    except Exception as e:
        print(e)

    db_methods.display_table_info(con, table_name)

    return None



def main():
    
    return None

if __name__ == "__main__":
    main()