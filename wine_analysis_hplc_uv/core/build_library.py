"""
Top level file to initialize a wine auth database from scratch.
"""
import os
import shutil

import duckdb as db
from numpy.random import f

from ..cellartracker_methods import cellartracker_cleaner, init_raw_cellartracker_table
from ..chemstation import chemstation_metadata_table_cleaner, process_chemstation
from ..core import adapt_super_pipe_to_db
from ..devtools import function_timer as ft
from ..devtools import project_settings
from ..sampletracker import init_raw_sample_tracker_table, sample_tracker_cleaner
from ..ux_methods import ux_methods as ux


@ft.timeit
def build_db_library(db_filepath: str, data_lib_path: str) -> None:
    """
    Pipeline function to construct the super_table, a cleaned algamation of chemstation, sample_tracker and cellartracker tables.
    """
    # 1. create db file if none exists.
    # dont use context management here because simply opening and closing a connection, forcing the creation of the .db file
    if not os.path.isfile(db_filepath):
        con = db.connect(db_filepath)
        con.close()

    # 2. remove a predefined list of files that exist inthe instrument 0_jono_data folder.
    delete_unwanted_files(data_lib_path)

    #  3. write raw tables to db from sources
    chemstation_metadata_table_name = "chemstation_metadata"
    chemstation_sc_table_name = "chromatogram_spectra"
    sampletracker_table_name = "sampletracker"
    cellartracker_table_name = "cellartracker"

    raw_chemstation_metadata_table_name = "raw_" + chemstation_metadata_table_name
    raw_chemstation_sc_table_name = "raw_" + chemstation_sc_table_name
    raw_sampletracker_table_name = "raw_" + sampletracker_table_name
    raw_cellartracker_table_name = "raw_" + cellartracker_table_name

    ux.ask_user_and_execute(
        "write raw tables?\n",
        write_raw_tables,
        data_lib_path,
        db_filepath,
        raw_chemstation_metadata_table_name,
        raw_chemstation_sc_table_name,
        raw_sampletracker_table_name,
        raw_cellartracker_table_name,
    )

    cleaned_chemstation_metadata_table_name = (
        "cleaned_" + chemstation_metadata_table_name
    )
    cleaned_sampletracker_table_name = "cleaned_" + sampletracker_table_name
    cleaned_cellartracker_table_name = "cleaned_" + cellartracker_table_name

    # 4. clean the raw tables
    ux.ask_user_and_execute(
        "write cleaned tables?\n",
        load_cleaned_tables,
        db_filepath,
        raw_chemstation_metadata_table_name,
        raw_sampletracker_table_name,
        raw_cellartracker_table_name,
        cleaned_chemstation_metadata_table_name,
        cleaned_sampletracker_table_name,
        cleaned_cellartracker_table_name,
    )

    super_tbl_name = "super_table"
    # 5. join the tables together.
    ux.ask_user_and_execute(
        "write super table?\n",
        adapt_super_pipe_to_db.load_super_table,
        db_filepath,
        table_1=cleaned_chemstation_metadata_table_name,
        table_2=cleaned_sampletracker_table_name,
        table_3=cleaned_cellartracker_table_name,
        tbl_name=super_tbl_name,
    )
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


def write_raw_tables(
    data_lib_path: str,
    db_filepath: str,
    chemstation_metadata_table_name: str,
    chemstation_sc_table_name: str,
    sampletracker_table_name: str,
    cellartracker_table_name: str,
):
    ux.ask_user_and_execute(
        "Writing chemstation data to db, proceed?",
        process_chemstation.process_chemstation,
        data_lib_path,
        db_filepath,
        chemstation_metadata_table_name,
        chemstation_sc_table_name,
    )
    ux.ask_user_and_execute(
        "Writing sampletracker data to db, proceed?",
        init_raw_sample_tracker_table.init_raw_sample_tracker_table,
        db_filepath,
        sampletracker_table_name,
    )

    ux.ask_user_and_execute(
        "Writing cellartracker data to db, proceed?",
        init_raw_cellartracker_table.init_raw_cellartracker_table,
        db_filepath,
        cellartracker_table_name,
    )
    return None


def load_cleaned_tables(
    db_filepath: str,
    raw_chemstation_metadata_table_name: str,
    raw_sampletracker_table_name: str,
    raw_cellartracker_table_name: str,
    cleaned_chemstation_metadata_table_name: str,
    cleaned_sampletracker_table_name: str,
    cleaned_cellartracker_table_name: str,
):
    # 1. Chemstation metadata table
    ux.ask_user_and_execute(
        f"Write {cleaned_chemstation_metadata_table_name} to db?",
        chemstation_metadata_table_cleaner.clean_ch_metadata_table,
        db_filepath,
        raw_chemstation_metadata_table_name,
        cleaned_chemstation_metadata_table_name,
    )

    # 2. Sampletracker table
    ux.ask_user_and_execute(
        f"Write {cleaned_sampletracker_table_name} to db?",
        sample_tracker_cleaner.clean_sample_tracker_table,
        db_filepath,
        raw_sampletracker_table_name,
        cleaned_sampletracker_table_name,
    )
    # 3. cellartracker table
    ux.ask_user_and_execute(
        f"Write {cleaned_cellartracker_table_name} to db?",
        cellartracker_cleaner.init_cleaned_cellartracker_table,
        db_filepath,
        raw_cellartracker_table_name,
        cleaned_cellartracker_table_name,
    )
    return None


def main():
    data_lib_path = "/Users/jonathan/0_jono_data"
    db_filepath = os.path.join(data_lib_path, "wine_auth_db.db")
    build_db_library(data_lib_path, db_filepath)


if __name__ == "__main__":
    main()
