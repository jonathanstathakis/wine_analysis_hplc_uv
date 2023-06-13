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

    logger.debug("Initializing multiprocessing pool...")
    pool = mp.Pool()

    logger.info(
        f"Processing {len(dirpaths)} directories using a multiprocessing pool..."
    )
    uv_files_dicts_list: List[
        Dict[str, Dict[str, str] | Dict[str, str | pd.DataFrame]]
    ] = pool.map(read_single_file.read_single_file, dirpaths)

    logger.debug("Closing and joining the multiprocessing pool...")
    pool.close()
    pool.join()

    uv_metadata_list: List = [file["metadata"] for file in uv_files_dicts_list]
    uv_data_list: List = [file["data"] for file in uv_files_dicts_list]

    def data_to_df(data_list: List) -> pd.DataFrame:
        def form_data_df(data_dict: Dict) -> pd.DataFrame:
            """
            Form a data df of format: [hash_column, [data_columns]] from the dict.
            """
            data_df: pd.DataFrame = data_dict["data"]
            data_df["hash_key"] = data_dict["hash_key"]

            return data_df

        data_hash_df_list = [form_data_df(data_dict) for data_dict in data_list]

        data_df: pd.DataFrame = pd.concat(data_hash_df_list, axis=0, ignore_index=True)

        return data_df

    metadata_df = pd.DataFrame(uv_metadata_list)
    data_df = data_to_df(uv_data_list)

    logger.info(f"Finished processing files..")
    return metadata_df, data_df
