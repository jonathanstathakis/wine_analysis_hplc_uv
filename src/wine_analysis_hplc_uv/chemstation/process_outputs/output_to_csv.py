"""
Output chemstation process data to csv.

TODO:
- [ ] write tests
- [ ] clean up pickling and other dev artifacts. 
"""
from typing import Tuple, Dict, List
import os
import shutil
import directory_tree
import pandas as pd
from wine_analysis_hplc_uv.chemstation import chemstationprocessor

# devimports, delete
import pickle


def data_lib_path():
    return "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files"


def chprocess_to_csv(
    metadata_df: pd.DataFrame,
    data_df: pd.DataFrame,
    data_lib_path: str,
    cleanup: bool = True,
    forceoverwrite: bool = False,
    wavelengths: List[str] = ["*"],
) -> None:
    # input vars
    processed_files_dirname: str = "processed_files"
    processed_files_root_path = os.path.join(data_lib_path, processed_files_dirname)

    if os.path.exists(processed_files_root_path):
        print(
            f"path exists at {processed_files_root_path}, since forceoverwrite set to {forceoverwrite}, deleting..\n"
        )
        shutil.rmtree(processed_files_root_path)

    # generate the intended filepaths

    # generate paths for the extracted data/metadata as strings of 'metadatapath' column
    metadata_df["metadatapath"] = create_metadata_outpath(
        path_series=metadata_df["path"],
        processed_files_root_path=processed_files_root_path,
        cleanup=cleanup,
    )

    # generate a metadata/data join table
    join_data_df = join_metadata_data(data_df=data_df, metadata_df=metadata_df)

    # create data outpaths
    join_data_df["datapath"] = join_data_df["metadatapath"].apply(create_data_outpath)

    # creates the directory tree that the data/metadata is destined to be in

    def make_target_dir(path_series: pd.Series, exist_ok: bool = False):
        path_series["parent_dir"] = os.path.dirname(path_series["metadatapath"])
        os.makedirs(path_series["parent_dir"], exist_ok=exist_ok)
        return None

    metadata_df.apply(make_target_dir, exist_ok=forceoverwrite, axis=1)

    # print the created directory tree structure from its root
    print("")
    print(f"Created directory tree at:\n\n{processed_files_root_path}\n\ntree:\n")
    directory_tree.display_tree(processed_files_root_path)
    print("")

    # functions to organise the data/metadata into a format appropriate for writing to csv
    # and writing them to the generated 'metadatapath'

    metadata_to_csv(metadata_df=metadata_df)

    data_to_csv(data_df=join_data_df, wavelengths=wavelengths)

    # print the created directory tree structure from its root
    print("")
    print(f"Created directory tree at:\n\n{processed_files_root_path}\n\ntree:\n")
    directory_tree.display_tree(processed_files_root_path)
    print("")
    cleanup = False

    if cleanup:
        shutil.rmtree(processed_files_root_path)

    return None


def join_metadata_data(
    data_df: pd.DataFrame, metadata_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Join the metadatapath column to the data df using the hash key.
    """

    join_data_df = pd.merge(
        left=metadata_df[["hash_key", "metadatapath"]],
        right=data_df,
        on="hash_key",
        how="left",
        validate="1:m",
    )
    # -1 because the join col is not duplicated
    assert (
        join_data_df.shape[1]
        == data_df.shape[1] + metadata_df[["hash_key", "metadatapath"]].shape[1] - 1
    ), "the result of the data_df and metadata_df join n should equal data_df n + metadata_df n"
    assert (
        join_data_df.shape[0] == data_df.shape[0]
    ), "the result of the join should have as many rows as input data_df"

    return join_data_df


def create_data_outpath(path: str) -> str:
    # here, we're removing the 'metadatapath' column from each group before saving it to a csv
    base, ext = os.path.splitext(os.path.basename(path))
    datafilename = base.replace("_metadata", "_data") + ".csv"
    datafilepath = os.path.join(os.path.dirname(path), datafilename)
    return datafilepath


def data_to_csv(data_df: pd.DataFrame, wavelengths: List[str] = ["*"]) -> None:
    # drop the first column (or the 'hash_key' column)

    # group your data by 'metadatapath' and apply a function to save each group to a csv

    for path, data in data_df.groupby("datapath"):
        if wavelengths[0] == "*":
            print(f"writing {path}..")
            basepath, ext = os.path.splitext(path)
            newfilepath = basepath + "_spectrum" + ext
            data.drop(columns=["datapath"]).to_csv(newfilepath, index=False)
            assert os.path.exists(newfilepath), "writing failed..\n"
        else:
            for wavelength in wavelengths:
                new_df = data.loc[:, ["mins", wavelength]]
                basepath, ext = os.path.splitext(path)
                newfilepath = basepath + "_" + wavelength + ext
                new_df["datapath"] = newfilepath
                print(f"writing {path}..")
                new_df.drop(columns=["datapath"]).to_csv(newfilepath, index=False)

    return None


def create_metadata_outpath(
    path_series: pd.Series, processed_files_root_path: str, cleanup: bool = True
) -> pd.Series:
    """
    Create a tree corresponding to the source data
    """

    # find the file root
    commonpath = os.path.commonpath(path_series.tolist())

    # # create new paths based on input root info

    def create_metadata_outpath(
        path: str, commonpath: str, processed_files_root_path: str
    ):
        relpath = os.path.relpath(path, commonpath)
        metadatapath = os.path.join(processed_files_root_path, relpath)
        filename = os.path.basename(metadatapath)
        filename, ext = os.path.splitext(filename)
        filename = filename + "_metadata" + ".csv"
        filepath = os.path.join(metadatapath, filename)
        return filepath

    metadatapath_series: pd.Series = path_series.apply(
        create_metadata_outpath, args=(commonpath, processed_files_root_path)
    )

    return metadatapath_series


def metadata_to_csv(metadata_df: pd.DataFrame) -> None:
    """_summary_
    Print metadata to individual csv files in the given metadatapaths
    Args:
        metadata_df (pd.DataFrame): _description_
    """

    def write_metadata_to_new_path(metadata_series: pd.Series):
        print(f"writing {metadata_series['metadatapath']}..")
        metadata_series.to_csv(metadata_series["metadatapath"], index_label="index")
        return metadata_series

    metadata_df.apply(write_metadata_to_new_path, axis=1)

    return None


def chprocess_pickle_interface(
    usechprocesspickle: bool, datadirpath: str, pkpath: str = ""
):
    if usechprocesspickle:
        if os.path.exists(pkpath):
            with open(pkpath, "rb") as f:
                chprocess = pickle.load(f)
        else:
            chprocess = chemstationprocessor.ChemstationProcessor(
                datadirpath, usepickle=False
            )

            with open(pkpath, "wb") as f:
                pickle.dump(chprocess, f)

    else:
        chprocess = chemstationprocessor.ChemstationProcessor(
            datadirpath, usepickle=False
        )
    return chprocess


def cleanup_pickle(pkpath: str, cleanup: bool) -> None:
    if cleanup:
        if os.path.exists(pkpath):
            print(f"removing chprocesspickle at {pkpath}")
            os.remove(pkpath)
        else:
            print("Warning: cleanup = True but no pickle to remove..\n")
    return None


def main():
    pkpath = os.path.join(data_lib_path(), "chprocesspickle.pk")

    chprocess = chemstationprocessor.ChemstationProcessor(datalibpath=data_lib_path())

    chprocess.to_csv_helper(
        wavelengths=["254", "450"], cleanup=True, forceoverwrite=True
    )

    cleanup_pickle(pkpath, True)

    return None


if __name__ == "__main__":
    main()
