"""
A submodule to handle chemstation data pickling to speed up testing and dev.
"""
import os
import pickle
import duckdb as db
from ..devtools import function_timer as ft
from ..devtools import project_settings
from . import init_chemstation_data_metadata


def chemstation_pickle_interface(
    pickle_filepath: str, uv_paths_list: list, con: db.DuckDBPyConnection
):
    # if pickle file exists, ask if want to use, or overwrite.
    if os.path.isfile(pickle_filepath):
        use_pickle = input("pickle found, use, or overwrite? (u/o): ")
        # if use pickle is selected, load pickle and continue program.
        if use_pickle == "u":
            chemstation_data_dicts_tuple = pickle_load(pickle_filepath)
            return chemstation_data_dicts_tuple
        # if overrwite is selected, deleted old pickle, run chemstation process, write new pickle
        elif use_pickle == "o":
            os.remove(pickle_filepath)
            chemstation_data_dicts_tuple = (
                init_chemstation_data_metadata.process_chemstation_uv_files(
                    uv_paths_list
                )
            )
            pickle_dump(chemstation_data_dicts_tuple, pickle_filepath)
    # if pickle doesnt exist, ask if want to create.
    elif not os.path.isfile(pickle_filepath):
        use_pickle = input(f"no pickle found, create? at {pickle_filepath} (y/n): ")
        # if yes to create, run chemstation process and create pickle.
        if use_pickle == "y":
            chemstation_data_dicts_tuple = (
                init_chemstation_data_metadata.process_chemstation_uv_files(
                    uv_paths_list
                )
            )
            pickle_dump(chemstation_data_dicts_tuple, pickle_filepath)
        # for any other response, just continue process.
        else:
            chemstation_data_dicts_tuple = (
                init_chemstation_data_metadata.process_chemstation_uv_files()
            )
        return chemstation_data_dicts_tuple
    else:
        use_pickle = input("no pickle found, would you like to create one? (y/n): ")
    return chemstation_data_dicts_tuple


def pickle_dump(obj, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(obj, f)
        return None


def pickle_load(filepath):
    with open(filepath, "rb") as f:
        obj = pickle.load(f)
        return obj


def pickle_path(
    pickle_fname: str = "chemstation_process.pk",
    pickle_jar_path: str = "chemstation_process_pickle_jar",
):
    pkg_root_filepath = os.path.abspath(__file__)
    pkg_root = os.path.dirname(pkg_root_filepath)

    pickle_jar_path = os.path.join(pkg_root, pickle_jar_path)

    if not os.path.isdir(pickle_jar_path):
        os.mkdir(pickle_jar_path)

    pickle_rel_path = os.path.join(pickle_jar_path, pickle_fname)

    pickle_path = os.path.join(pkg_root, pickle_rel_path)
    return pickle_path


def main():
    return None


if __name__ == "__main__":
    main()
