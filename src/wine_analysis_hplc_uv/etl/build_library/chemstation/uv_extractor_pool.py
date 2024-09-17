from typing import List, Dict
import multiprocessing as mp
import pandas as pd
from wine_analysis_hplc_uv.etl.build_library.chemstation import read_single_file
import logging

logger = logging.getLogger(__name__)

def form_data_df(data_dict: Dict) -> pd.DataFrame:
    """
    Form a data df of format:
    [hash_column, data_column1, data_column2,..,data]from the dict.
    """
    data_df: pd.DataFrame = data_dict["data"]
    data_df["id"] = data_dict["id"]

    for label in ("id", "mins"):
        assert label in data_df.columns, data_df.columns

    logging.debug(f"\n{data_df.columns}")

    data_df = (
        data_df.melt(
            id_vars=["mins", "id"],
            var_name="wavelength",
            value_name="absorbance",
            )
        .assign(wavelength=lambda df: "nm_" + df.wavelength)
        .pivot_table(
            columns=["wavelength"], values="absorbance", index=["id", "mins"]
        )
        .reset_index()
        )

    return data_df

def dict_list_to_long_df(data_list: List) -> pd.DataFrame:
        
            
    logger.info("converting the data dict to a long df..")
    data_hash_df_list = [form_data_df(data_dict) for data_dict in data_list]

    data_df: pd.DataFrame = pd.concat(data_hash_df_list, axis=0, ignore_index=True)

    return data_df


def uv_extractor_pool(
    dirpaths: List[str],
) -> List[Dict[str, Dict[str, str] | Dict[str, str | pd.DataFrame]]]:
    """
    Form a multiprocess pool to apply uv_extractor,
    returning a tuple of dicts for each .D file in the dirpath my logger.info("Processing files..")
    
    with mp.Pool() as pool:
        uv_files_dicts_list = pool.map(read_single_file.read_single_file, dirpaths)
        logger.debug("Closing and joining the multiprocessing pool..")
    
    uv_metadata_list: List = [file["metadata"] for file in uv_files_dicts_list]
    uv_data_list: List = [file["data"] for file in uv_files_dicts_list]
    
    metadata_df = pd.DataFrame(uv_metadata_list)
    data_df = dict_list_to_long_df(uv_data_list)

    return metadata_df, data_df
