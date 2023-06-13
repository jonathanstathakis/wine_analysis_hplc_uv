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
    uv_file_dicts: List[
        Dict[str, Dict[str, str] | Dict[str, str | pd.DataFrame]]
    ] = pool.map(read_single_file.read_single_file, dirpaths)

    logger.debug("Closing and joining the multiprocessing pool...")
    pool.close()
    pool.join()

    logger.info(f"Finished processing files..")
    return uv_file_dicts
