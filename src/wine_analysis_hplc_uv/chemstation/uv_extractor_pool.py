import json
import os
import uuid
from typing import List, Tuple, Dict, Union
import multiprocessing as mp
import numpy as np
import pandas as pd

from wine_analysis_hplc_uv.chemstation import logger, read_single_file


def uv_extractor_pool(
    dirpaths: List[str],
) -> List[Dict[str, Dict[str, str] | Dict[str, str | pd.DataFrame]]]:
    """
    Form a multiprocess pool to apply uv_extractor, returning a tuple of dicts for each .D file in the dirpath list.
    """
    logger.info("Processing files..")
    logger.debug(f"{__file__}")

    logger.debug("Initializing multiprocessing pool...")

    logger.info(
        f"Using the multiprocessing pool to process {len(dirpaths)} directories.."
    )
    with mp.Pool() as pool:
        uv_files_dicts_list = pool.map(read_single_file.read_single_file, dirpaths)
        logger.debug("Closing and joining the multiprocessing pool..")

    uv_metadata_list: List = [file["metadata"] for file in uv_files_dicts_list]
    uv_data_list: List = [file["data"] for file in uv_files_dicts_list]

    def dict_list_to_long_df(data_list: List) -> pd.DataFrame:
        def form_data_df(data_dict: Dict) -> pd.DataFrame:
            """
            Form a data df of format: [hash_column, [data_columns]] from the dict.
            """
            data_df: pd.DataFrame = data_dict["data"]
            data_df["hash_key"] = data_dict["hash_key"]

            data_df = data_df.melt(
                id_vars=["hash_key", "mins"],
                var_name="wavelength (nm)",
                value_name="value",
            )  # TODO: 2023-06-13 15:34:45 - need to build in a method of handling files that fail to parse so that they are still present in the resulting db table. To do this, will need to id the empty dfs, add the missing colnames with empty values so they will melt too.

            data_df["wavelength (nm)"] = pd.to_numeric(data_df["wavelength (nm)"])

            return data_df

        data_hash_df_list = [form_data_df(data_dict) for data_dict in data_list]

        data_df: pd.DataFrame = pd.concat(data_hash_df_list, axis=0, ignore_index=True)

        return data_df

    metadata_df = pd.DataFrame(uv_metadata_list)
    data_df = dict_list_to_long_df(uv_data_list)

    logger.info(f"Finished processing files..")
    return metadata_df, data_df
