"""
All the methods used to preprocess the chemstation files into the db
"""
import os
import fnmatch
from devtools import function_timer as ft


@ft.timeit
def uv_filepaths_to_list(root_dir_path: str) -> list:
    """
    Take a filepath and search it for .D dirs containing .UV files. Returns a list of filepaths matching the criteria.
    """
    # Create an empty list to store the matching directory paths
    dirpaths = []
    filepath_suffix = ".UV"

    print(f"Walking through {root_dir_path} to find {filepath_suffix} files", end=" ")
    # Walk through the directory tree using os.walk()
    for dirpath, dirnames, filenames in os.walk(root_dir_path):
        # Check if the directory name ends with '.D'

        if dirpath.endswith(".D"):
            # Check if there is at least one file in the directory that ends with '.UV'
            if any(fnmatch.fnmatch(file, "*.UV") for file in filenames):
                # If both conditions are met, append the directory path to the list
                dirpaths.append(dirpath)

    print(f"Found {len(dirpaths)} .UV files")

    return dirpaths


def main():
    return None


if __name__ == "__main__":
    main()
