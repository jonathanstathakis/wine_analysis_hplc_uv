"""
An entry function for chemstation file processing.

The current process from entry to writing the raw chemstation tables
to db are as follows:

1. entry_func:
    takes the data_lib_path and db con object, gets the pickle file filepath.
2. uv_filepaths_to_list:
    for the data_lib_path, find the absolute filepath of all .D directories containing .UV files.
3. check_if_chemstation_table_needs_updating: check if any of the paths in uv_paths_list arnt currently in the db.
4. pickle_interface:
    if pickle file of the processed data objects exists, ask if to load from that, otherwise if overwrite is chosen, run process_chemstation_uv_files.
5. back to entry_func:
    if a tuple is returned from pickle_interface (just a typecheck to ensure correct procedure) call write_chemstation_data_to_db_entry.
6. write_chemstation_data_to_db_entry:
    check types, pass the data dict lists to write_chemstation_to_db
7. write_chemstation_to_db:
    pass metadata_list to to chemstation_metadata_to_db, pass spectra_list to chromatogram_spectra_to_db
8.
    i. chemstation_metadata_to_db:
        1. metadata_list_to_df
        2. check_if_table_exists_write_df_to_db
    ii. chromatogram_spectra_to_db:
        1. uv_data_list_to_df
        2. check_if_table_exists_write_df_to_db

 the list of files to process, calls the processor, passes the processed data to the pickler, passes the processed data to the db writing function.
"""
import os
import duckdb as db
import pandas as pd
from ..chemstation import (
    chemstation_methods,
    chemstation_to_db_methods,
    pickle_chemstation_data,
)
from ..db_methods import db_methods
from ..devtools import function_timer as ft
from ..devtools import project_settings


def chemstation_data_to_db(
    data_lib_path: str,
    db_filepath: str,
    raw_chemstation_metadata_table_name: str,
    raw_chemstation_spectra_table_name: str,
):
    """
    main driver file, handle any preprocessing then activate write_ch_metadata_table_to_db_entry.
    """
    # get the .D paths
    # check if any paths are already in the db, returns the list of those NOT in the db.

    print("###\n\nChemstation Raw Data Processing\n\n###\n")

    uv_paths_list = chemstation_methods.uv_filepaths_to_list(data_lib_path)
    uv_paths_list = check_if_chemstation_tables_needs_updating(
        uv_paths_list, db_filepath, raw_chemstation_metadata_table_name
    )
    # if uv_paths_list is empty, skip rest of function.
    if uv_paths_list:
        # get the uv_metadata and data as lists either from the pickle or the process.
        # pickle vars
        pickle_filename = "chemstation_data_dicts_tuple.pk"

        pickle_filepath = pickle_chemstation_data.pickle_path(pickle_filename)
        chemstation_data_dicts_tuple = (
            pickle_chemstation_data.chemstation_pickle_interface(
                pickle_filepath, uv_paths_list, db_filepath
            )
        )

        assert isinstance(
            chemstation_data_dicts_tuple, tuple
        ), f"the data_dicts var is expected to be of type tuple, but {type(chemstation_data_dicts_tuple)}"

        chemstation_metadata_list, chromatogram_spectrum_list = (
            chemstation_data_dicts_tuple[0],
            chemstation_data_dicts_tuple[1],
        )

        # extract the lists from the list object
        assert isinstance(chemstation_metadata_list, tuple) & isinstance(
            chromatogram_spectrum_list, tuple
        ), f"chemstation_metadata_list is dtype {type(chemstation_metadata_list)}, chromatogram_spectrum_list is dtype {type(chromatogram_spectrum_list)}. Both should be list"

        metadata_df = chemstation_to_db_methods.metadata_list_to_df(
            chemstation_metadata_list
        )
        # cs: spectrum_chromatogram
        cs_df = chemstation_to_db_methods.uv_data_list_to_df(chromatogram_spectrum_list)

        # metadata_df.pipe
        metadata_df.pipe(
            db_methods.append_df_to_db_table_handler,
            db_filepath,
            raw_chemstation_metadata_table_name,
        )
        cs_df.pipe(
            db_methods.append_df_to_db_table_handler,
            db_filepath,
            raw_chemstation_spectra_table_name,
        )
    elif not uv_paths_list:
        print(f"{len(uv_paths_list)} new uv_files to add to db.\n")
        print(
            f"Therefore, skipping remaining raw chemstation process. {os.path.abspath(__file__)}\n"
        )
        return None
    pickle_cleanup(pickle_filepath)
    print("###\n\nEND CHEMSTATION RAW DATA PROCESSING\n\n###\n")
    return None


def pickle_cleanup(pickle_filepath: str) -> None:
    print("Cleaning up process pickle after writing data to db..")
    os.remove(pickle_filepath)


def check_if_chemstation_tables_needs_updating(
    uv_paths_list: list, db_filepath: str, db_table_name: str
) -> list:
    """
    Check if the path column of the chemstation db table corresponds to the uv_paths_list. if any in uv_paths_list not in db, tell user.
    """
    print(f"checking if any files in uv_paths_list not in {db_table_name}..\n")

    query = f"""
    SELECT
        path
    FROM
        {db_table_name}
    """

    uv_paths_series = pd.Series(uv_paths_list)

    assert os.path.isfile(db_filepath), "db file not found"

    try:
        assert db_methods.test_db_table_exists(db_filepath, db_table_name)
    except:
        print("table not found, continuing..\n")
        return uv_paths_list

    # try to connect to the db table provided and extract the paths column as a pd series
    try:
        print(f"connecting to {db_filepath}..\n")

        with db.connect(db_filepath) as con:
            db_path_series = con.sql(query).df()["path"]
            print(
                f'in {db_table_name}, {len(uv_paths_series)} rows of "path" found..\n'
            )

    except db.CatalogException as e:
        print(e)
        with db.connect(db_filepath) as con:
            con.sql("SELECT name FROM sqlite_master WHERE type='table'").show()
        return uv_paths_list

    uv_paths_list = uv_paths_series[~uv_paths_series.isin(db_path_series)].to_list()

    print(f'{uv_paths_list} not found in db "path" column..\n')

    try:
        assert uv_paths_list

    except AssertionError as e:
        print(e)
        return uv_paths_list
    else:
        print(
            f"The following files are in the specified filepath but are not in {db_table_name}:\n"
        )
        print(uv_paths_list)
    finally:
        return uv_paths_list


def main():
    return None


if __name__ == "__main__":
    main()
