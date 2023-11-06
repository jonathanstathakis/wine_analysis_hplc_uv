from typing import List, Dict
import multiprocessing as mp
import pandas as pd
from wine_analysis_hplc_uv.chemstation import read_single_file
import logging

logger = logging.getLogger(__name__)


def uv_extractor_pool(
    dirpaths: List[str],
) -> List[Dict[str, Dict[str, str] | Dict[str, str | pd.DataFrame]]]:
    """
    Form a multiprocess pool to apply uv_extractor,
    returning a tuple of dicts for each .D file in the dirpath list.
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

    logger.info("after multiprocess, len(uv_files_dict_list) = {uv_files_dict_list}")
    assert len(uv_files_dicts_list) > 0
    uv_metadata_list: List = [file["metadata"] for file in uv_files_dicts_list]
    uv_data_list: List = [file["data"] for file in uv_files_dicts_list]
    assert len(uv_metadata_list) > 0
    assert len(uv_data_list) > 0

    def dict_list_to_long_df(data_list: List) -> pd.DataFrame:
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
            # data_df = data_df.melt(
            #     id_vars=["id", "mins"],
            #     var_name="wavelength",
            #     value_name="value",
            # )

            # .pivot_table(index=['id','mins'],columns=[''])
            # TODO: 2023-06-13 15:34:45 -
            # need to build in a method of handling files that fail to
            # parse so that they are still present in the resulting db table.
            # To do this, will need to id the empty dfs, add the missing
            # colnames with empty values so they will melt too.

            # data_df["wavelength"] = pd.to_numeric(data_df["wavelength"])

            return data_df

        logger.info("converting the data dict to a long df..")
        data_hash_df_list = [form_data_df(data_dict) for data_dict in data_list]

        data_df: pd.DataFrame = pd.concat(data_hash_df_list, axis=0, ignore_index=True)

        assert isinstance(data_df, pd.DataFrame)

        return data_df

    metadata_df = pd.DataFrame(uv_metadata_list)
    data_df = dict_list_to_long_df(uv_data_list)

    logger.info("Finished processing files..")
    return metadata_df, data_df
