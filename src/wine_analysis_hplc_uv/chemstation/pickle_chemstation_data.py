"""
A submodule to handle chemstation data pickling to speed up testing and dev.
"""
import os
import pickle
from typing import List, Tuple

import duckdb as db

from wine_analysis_hplc_uv.devtools import function_timer as ft
from wine_analysis_hplc_uv.devtools import project_settings
from wine_analysis_hplc_uv.chemstation import process_chemstation


def process_and_pickle(uv_paths_list: List[str], pickle_filepath: str) -> Tuple[list[dict], list[dict]]:
    chemstation_data_dicts_tuple = process_chemstation.process_chemstation_uv_files(uv_paths_list)
    os.makedirs(os.path.dirname(pickle_filepath), exist_ok=True)
    pickle_dump(chemstation_data_dicts_tuple, pickle_filepath)
    return chemstation_data_dicts_tuple

def pickle_interface(pickle_filepath: str, uv_paths_list: List[str]) -> Tuple[list[dict], list[dict]]:
    """
    
    
    Args:
        pickle_filepath (str): _description_
        uv_paths_list (List[str]): _description_

    Returns:
        Tuple[list[dict], list[dict]]: _description_
    """
    actions = {
        "u": lambda: pickle_load(pickle_filepath),
        "o": lambda: process_and_pickle(uv_paths_list=uv_paths_list, pickle_filepath=pickle_filepath),
        "y": lambda: process_and_pickle(uv_paths_list=uv_paths_list, pickle_filepath=pickle_filepath),
        "n": lambda: process_chemstation.process_chemstation_uv_files(uv_paths_list=uv_paths_list),
    }

    if os.path.isfile(pickle_filepath):
        action_key: str = input("pickle found, use, or overwrite? (u/o): ")
    else:
        action_key = input(f"no pickle found, create? at {pickle_filepath} (y/n): ")
    
    action = actions.get(action_key, actions["n"])
    return action()



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
