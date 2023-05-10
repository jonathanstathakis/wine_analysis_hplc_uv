"""
Top level file to initialize a wine auth database from scratch.
"""
import os
import duckdb as db
import sys

sys.path.append('../')

import init_chemstation_data_metadata as ch
from init_raw_sample_tracker_table import init_raw_sample_tracker_table
from init_raw_cellartracker_table import init_raw_cellartracker_table
from chemstation_metadata_table_cleaner import init_cleaned_chemstation_metadata_table
from sample_tracker_cleaner import init_cleaned_sample_tracker_table
from cellartracker_cleaner import init_cleaned_cellartracker_table
import function_timer as ft
import adapt_super_pipe_to_db
import shutil
import function_timer as ft

def delete_files(data_lib_path : str):
    """
    There is a list of runs which are persistant across the instrument and local storage. ATM easier to delete them here than manually.
    """
    dirs_to_delete = [
     '2023-02-22_2021-DEBORTOLI-CABERNET-MERLOT_HALO.D',
     '2023-02-22_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D',
     '0_2023-04-12_wine-deg-study/startup-sequence-results/'
    ]
    def delete_dirs(dirpath : str):
        if os.path.isdir(dirpath):
            print(f'deleting{dirpath}')
            shutil.rmtree(dirpath)
        return None
    
    [delete_dirs(os.path.join(data_lib_path, dir)) for dir in dirs_to_delete]

    return None

@ft.timeit
def build_library(db_path : str, data_lib_path : str) -> None:
    """
    Pipeline function to construct the super_table, a cleaned algamation of chemstation, sample_tracker and cellartracker tables.

    1. Remove existing database file.
    2. delete specified files from data dir if present.
    3. get a list of .D dir paths containing .UV files.
    3. write raw tables.
    4. write cleaned tables.
    5. write super table.
    """
    remove_existing_db(db_path)
    delete_files(data_lib_path)

    # get the list of .D dir filepaths containing .UV files.

    with db.connect(f'{db_path}') as con:
            load_raw_tables(con, data_lib_path)
            load_cleaned_tables(con)
            adapt_super_pipe_to_db.load_super_table(con)
            con.sql('DESCRIBE').show()
    return None

def remove_existing_db(db_path : str) -> None:
    # remove old db if it exists.
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"deleted {db_path}")
    return None

def load_raw_tables(con, data_lib_path):
    ch.init_chemstation_data_metadata_tables(data_lib_path, con)
    init_raw_sample_tracker_table(con)
    init_raw_cellartracker_table(con)
    return None

def load_cleaned_tables(con):
    init_cleaned_chemstation_metadata_table(con, 'raw_chemstation_metadata')
    init_cleaned_sample_tracker_table(con, 'raw_sample_tracker')
    init_cleaned_cellartracker_table(con, 'raw_cellartracker')
    return None

def main():
    build_library(db_path = 'wine_auth_db.db', data_lib_path = "/Users/jonathan/0_jono_data"
)

if __name__ == "__main__":
    main()