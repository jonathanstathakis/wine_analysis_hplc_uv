"""

"""
import os
from typing import List, Tuple, Any

from wine_analysis_hplc_uv.chemstation import (
    chemstation_methods,
    chemstation_to_db_methods,
    pickle_chemstation_data,
)
from wine_analysis_hplc_uv.chemstation import ch_data_multiprocess
from wine_analysis_hplc_uv.chemstation import logger


def process_chemstation_uv_files(
    uv_paths_list: List[str],
) -> Tuple[List[dict], List[dict]]:
    logger.info("Processing files..")
    logger.debug(f"{__file__}")
    uv_metadata_list, uv_data_list = ch_data_multiprocess.ch_data_multiprocess(
        uv_paths_list
    )
    return uv_metadata_list, uv_data_list


def main():
    return None


if __name__ == "__main__":
    main()
