"""
A submodule to handle chemstation data pickling to speed up testing and dev.
"""

import os
import pickle
from typing import List, Tuple


from . import init_chemstation_data_metadata


def pickle_interface(
    pickle_filepath: str, uv_paths_list: List[str]
) -> Tuple[list[dict], list[dict]]:
    # if pickle file exists, ask if want to use, or overwrite.
    if os.path.isfile(pickle_filepath):
        overwrite_pickle = input("pickle found, use, or overwrite? (u/o): ")
        print("")
        # if use pickle is selected, load pickle and continue program.
        if overwrite_pickle == "u":
            chemstation_data_dicts_tuple = pickle_load(pickle_filepath)
            return chemstation_data_dicts_tuple
        # if overrwite is selected, deleted old pickle, run chemstation process, write new pickle
        elif overwrite_pickle == "o":
            print(f"{__file__}\n\nremoving {pickle_filepath}..\n")
            os.remove(pickle_filepath)

            chemstation_data_dicts_tuple = (
                init_chemstation_data_metadata.process_chemstation_uv_files(
                    uv_paths_list
                )
            )
            assert (
                chemstation_data_dicts_tuple
            ), f"{__file__} chemstation_data_dicts_tuple is empty..\n"
            pickle_dump(chemstation_data_dicts_tuple, pickle_filepath)
            return chemstation_data_dicts_tuple
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
            os.mkdir(os.path.dirname(pickle_filepath))
            pickle_dump(chemstation_data_dicts_tuple, pickle_filepath)
        # for any other response, just continue process.
        else:
            chemstation_data_dicts_tuple = (
                init_chemstation_data_metadata.process_chemstation_uv_files()
            )
        return chemstation_data_dicts_tuple
    else:
        use_pickle = input("no pickle found, would you like to create one? (y/n): ")
    return None


def pickle_dump(obj: object, filepath: str) -> None:
    with open(filepath, "wb") as f:
        pickle.dump(obj, f)
        return None


def pickle_load(filepath: str) -> object:
    with open(filepath, "rb") as f:
        obj = pickle.load(f)
        return obj


def main():
    return None


if __name__ == "__main__":
    main()
