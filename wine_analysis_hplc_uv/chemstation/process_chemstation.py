"""
An entry function for chemstation file processing
"""
import os

import duckdb as db

from ..chemstation import (
    chemstation_methods,
    chemstation_to_db_methods,
    pickle_chemstation_data,
)
from ..devtools import function_timer as ft
from ..devtools import project_settings


def process_chemstation(
    data_lib_path: str, db_filepath: str, ch_metadata_tblname: str, ch_sc_tblname: str
):
    """
    main driver file, handle any preprocessing then activate write_ch_metadata_table_to_db_entry.
    """
    # pickle vars
    pickle_filename = "chemstation_data_dicts_tuple.pk"
    pickle_filepath = os.path.join(os.getcwd(), pickle_filename)

    # get the .D paths
    uv_paths_list = chemstation_methods.uv_filepaths_to_list(data_lib_path)

    # get the uv_metadata and data as lists either from the pickle or the process
    chemstation_data_dicts_tuple = pickle_chemstation_data.pickle_interface(
        pickle_filepath, uv_paths_list, db_filepath
    )

    # write the uv_metadata and data to tables in the given db.
    chemstation_to_db_methods.write_chemstation_data_to_db_entry(
        chemstation_data_dicts_tuple, db_filepath, ch_metadata_tblname, ch_sc_tblname
    )

    return None


def main():
    return None


if __name__ == "__main__":
    main()
