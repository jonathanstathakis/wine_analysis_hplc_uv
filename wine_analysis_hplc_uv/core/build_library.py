"""
Top level file to initialize a wine auth database from scratch.
"""
import os
import shutil
import duckdb as db
from ..devtools import function_timer as ft, project_settings
from ..cellartracker_methods import cellartracker_cleaner, init_raw_cellartracker_table
from ..chemstation import chemstation_process_entry, init_chemstation_data_metadata
from ..core import adapt_super_pipe_to_db
from ..sampletracker import init_raw_sample_tracker_table, sample_tracker_cleaner


@ft.timeit
def build_db_library(db_filepath: str, data_lib_path: str) -> None:
    """
    Pipeline function to construct the super_table, a cleaned algamation of chemstation, sample_tracker and cellartracker tables.

    1. Create db if none exists.
    1. delete specified files from data dir if present.
    2. get a list of .D dir paths containing .UV files.
    3. write raw tables.
    4. write cleaned tables.
    5. write super table.
    """
    # create db file if none exists.
    if not os.path.isfile(db_filepath):
        con = db.connect(db_filepath)
        con.close()

    # remove a predefined list of files that exist inthe instrument 0_jono_data folder.
    delete_unwanted_files(data_lib_path)

    write_raw_tables(data_lib_path, db_filepath)
    # load_cleaned_tables(con)
    # adapt_super_pipe_to_db.load_super_table(con)
    # con.sql('DESCRIBE').show()
    return None


def delete_unwanted_files(data_lib_path: str):
    """
    There is a list of runs which are persistant across the instrument and local storage. ATM easier to delete them here than manually.
    """
    dirs_to_delete = [
        "2023-02-22_2021-DEBORTOLI-CABERNET-MERLOT_HALO.D",
        "2023-02-22_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D",
        "0_2023-04-12_wine-deg-study/startup-sequence-results/",
    ]

    def delete_dirs(dirpath: str):
        if os.path.isdir(dirpath):
            print(f"deleting{dirpath}")
            shutil.rmtree(dirpath)
        return None

    [delete_dirs(os.path.join(data_lib_path, dir)) for dir in dirs_to_delete]

    return None


def remove_existing_db(db_path: str) -> None:
    # remove old db if it exists.
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"deleted {db_path}")
    return None


def write_raw_tables(data_lib_path: str, db_filepath: str):
    #chemstation_process_entry.chemstation_data_to_db(data_lib_path, db_filepath)
    init_raw_sample_tracker_table.init_raw_sample_tracker_table(db_filepath)
    # init_raw_cellartracker_table(con)
    return None


def load_cleaned_tables(con):
    init_cleaned_chemstation_metadata_table.init_raw_sample_tracker_table(
        con, "raw_chemstation_metadata"
    )
    # sample_tracker_cleaner.init_cleaned_sample_tracker_table(con, 'raw_sample_tracker')
    # cellartracker_cleaner.init_cleaned_cellartracker_table(con, 'raw_cellartracker')
    return None


def main():
    build_db_library(
        db_filepath="wine_auth_db.db", data_lib_path="/Users/jonathan/0_jono_data"
    )


if __name__ == "__main__":
    main()
