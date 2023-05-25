"""

"""
import os
from typing import List, Tuple, Any

from . import chemstation_methods, chemstation_to_db_methods, pickle_chemstation_data
from . import ch_data_multiprocess


def chemstation(
    data_lib_path: str, db_filepath: str, ch_metadata_tblname: str, ch_sc_tblname: str
):
    """
    main driver file, handle any preprocessing then activate write_ch_metadata_table_to_db_entry.
    """
    # pickle vars
    pickle_filename = "chemstation_process_picklejar/chemstation_data_dicts_tuple.pk"
    pickle_filepath = os.path.join(data_lib_path, pickle_filename)

    # get the .D paths
    uv_paths_list: list[str] = chemstation_methods.uv_filepaths_to_list(root_dir_path=data_lib_path)

    # get the uv_metadata and data as lists either from the pickle or the process
    ch_data: Tuple[List[dict], List[dict]] = pickle_chemstation_data.pickle_interface(
        pickle_filepath, uv_paths_list
    )

    # write the uv_metadata and data to tables in the given db.
    chemstation_to_db_methods.write_chemstation_data_to_db_entry(
        ch_data, db_filepath, ch_metadata_tblname, ch_sc_tblname
    )

    return None


def process_chemstation_uv_files(uv_paths_list: List[str]) -> Tuple[List[dict], List[dict]]:
    print(f"{__file__}\n\nProcessing files..\n")
    uv_metadata_list, uv_data_list = ch_data_multiprocess.ch_data_multiprocess(uv_paths_list)
    return uv_metadata_list, uv_data_list


def main():    
    return None


if __name__ == "__main__":    
    main()
