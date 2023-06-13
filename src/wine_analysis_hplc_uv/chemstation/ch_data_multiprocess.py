from typing import List, Tuple, Dict
import collections
from wine_analysis_hplc_uv.chemstation import uv_extractor_pool
import pandas as pd

from wine_analysis_hplc_uv.chemstation import logger


def ch_data_multiprocess(dirpath_list: List[str]) -> Tuple[List[dict], List[dict]]:
    """
    1. Create the metadata and data dicts from each .D file.
    2. check that the hash keys are unique.
    3. return uv_metadata_list and uv_data_list
    """
    logger.info("Processing files..")
    logger.debug(f"{__file__}")

    uv_metadata_list, uv_data_list = uv_extractor_pool.uv_extractor_pool(
        dirpaths=dirpath_list
    )

    def test_dup_hash_keys(uv_metadata_list: List[dict]) -> None:
        # observe how many unique hash_keys were generated. duplicates are probably caused by duplicate files/filenames.
        logger.debug("size of metadata_list", len(uv_metadata_list))

        # print the UUIDs that occur more than once.
        list_of_keys: List[str] = [d["hash_key"] for d in uv_metadata_list]
        uuid_counts = collections.Counter(list_of_keys)
        duplicates: List[str] = [
            uuid for uuid, count in uuid_counts.items() if count > 1
        ]
        logger.debug("Duplicate UUIDs:", len(duplicates))

        for uuid in duplicates:
            print(uuid)
            for metadata_dict in uv_metadata_list:
                if uuid == metadata_dict["hash_key"]:
                    print(f"duplicate UUID generated by: {metadata_dict['path']}")
        return None

    test_dup_hash_keys(uv_metadata_list=uv_metadata_list)

    return uv_metadata_list, uv_data_list
