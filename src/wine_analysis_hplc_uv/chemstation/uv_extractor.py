import json
import os
import uuid
from typing import List, Tuple, Dict, Union
import multiprocessing as mp
import numpy as np
import pandas as pd
import rainbow as rb
from wine_analysis_hplc_uv.chemstation import logger

counter = None
counter_lock = None


def extract_data(
    path: str,
) -> Dict[str, Union[Dict[str, str], Dict[str, Union[str, pd.DataFrame]]]]:
    """
    Form two dicts linked by a hash_key for each chemstation .D dir, representing a run.
    Takes a filepath as a str, returns a tuple of dicts, metadata_dict and uv_data_dict.

    metadata_dict contains 'path', 'sequence_name', 'hash_key' items. uv_data_dict contains 'data' and 'hash_key' items.
    """
    uv_name = "DAD1.UV"
    global counter, counter_lock

    if os.path.isfile(path=os.path.join(path, uv_name)):
        uv_file = rb.read(path=path).get_file(filename=uv_name)

        metadata_dict: Dict[str, str] = uv_file.metadata
        metadata_dict["path"] = path
        metadata_dict["sequence_name"] = get_sequence_name(metadata_dict["path"])
        metadata_dict["hash_key"] = primary_key_generator(metadata_dict)

        uv_data_dict = {}
        uv_data_dict["data"] = uv_data_to_df(uv_file=uv_file)
        uv_data_dict["hash_key"] = metadata_dict["hash_key"]

        with counter_lock:
            counter.value += 1
            logger.debug(
                f"Processed {metadata_dict['path']}. Have processed {counter.value} files."
            )
    else:
        logger.warning(f"{path} does not contain a .UV file. Remove from the library?")

    returndict: Dict[
        str, Union[Dict[str, str], Dict[str, Union[str, pd.DataFrame]]]
    ] = {
        "metadata": metadata_dict,
        "data": uv_data_dict,
    }

    return returndict


def get_sequence_name(path: str) -> str:
    parent = os.path.dirname(path)
    if "sequence.acaml" in os.listdir(parent):
        sequence_name = os.path.basename(parent)
    else:
        sequence_name = "single_run"

    return sequence_name


def primary_key_generator(metadata_dict):
    data_json = json.dumps(metadata_dict["date"], sort_keys=True)
    unique_id = uuid.uuid5(uuid.NAMESPACE_URL, data_json)
    return str(unique_id).replace("-", "_")


def uv_data_to_df(uv_file: rb.DataFile) -> pd.DataFrame:
    spectrum = np.concatenate((uv_file.xlabels.reshape(-1, 1), uv_file.data), axis=1)

    column_names = ["mins"] + list(uv_file.ylabels)
    column_names = [str(name) for name in column_names]

    an_index = np.arange(0, spectrum.shape[0])

    try:
        df = pd.DataFrame(data=spectrum, columns=column_names, index=an_index)
        return df
    except Exception as e:
        logger.error(e)
        logger.error(uv_file.metadata.get("notebook"), uv_file.metadata.get("date"))


def uv_extractor_pool(
    dirpaths: List[str],
) -> List[Dict[str, Dict[str, str] | Dict[str, str | pd.DataFrame]]]:
    """
    Form a multiprocess pool to apply uv_extractor, returning a tuple of dicts for each .D file in the dirpath list.
    """
    global counter, counter_lock
    counter = mp.Value("i", 0)  # 'i' indicates an integer
    counter_lock = mp.Lock()

    logger.debug("Initializing multiprocessing pool...")
    pool = mp.Pool(initializer=init_pool, initargs=(counter, counter_lock))

    logger.info(
        f"Processing {len(dirpaths)} directories using a multiprocessing pool..."
    )
    uv_file_dicts: List[
        Dict[str, Dict[str, str] | Dict[str, str | pd.DataFrame]]
    ] = pool.map(extract_data, dirpaths)

    logger.debug("Closing and joining the multiprocessing pool...")
    pool.close()
    pool.join()

    logger.info(f"Finished processing files..")
    return uv_file_dicts


def init_pool(c, l) -> None:
    global counter, counter_lock
    counter = c
    counter_lock = l
