from importlib import metadata
import json
import os
import uuid
from typing import List, Tuple, Dict, Union
import rainbow as rb
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def read_single_file(
    path: str,
) -> Dict[str, Union[Dict[str, str], Dict[str, Union[str, pd.DataFrame]]]]:
    """
    Form two dicts linked by a hash_key for each chemstation .D dir, representing a run.
    Takes a filepath as a str, returns a tuple of dicts, metadata_dict and uv_data_dict.

    metadata_dict contains 'path', 'sequence_name', 'hash_key' items. uv_data_dict contains 'data' and 'hash_key' items.
    """

    def uv_data_to_df(uv_file: rb.DataFile) -> pd.DataFrame:
        """
        requires a parsed `rb.DataFile` as input, outputs a df.
        """
        spectrum = np.concatenate(
            (uv_file.xlabels.reshape(-1, 1), uv_file.data), axis=1
        )

        column_names = ["mins"] + list(uv_file.ylabels)
        column_names = [str(name) for name in column_names]

        an_index = np.arange(0, spectrum.shape[0])

        try:
            df = pd.DataFrame(data=spectrum, columns=column_names, index=an_index)

            return df
        except Exception as e:
            logger.error(e)
            logger.error(uv_file.metadata.get("notebook"), uv_file.metadata.get("date"))
            return None

    uv_name = "DAD1.UV"

    assert os.path.isfile(path=os.path.join(path, uv_name))

    metadata_dict = dict(
        path=path,
    )

    uv_data_dict = dict(
        data=pd.DataFrame(),
        id="",
    )

    # try:
    datadir = rb.read(path=path)
    uv_file = datadir.get_file(filename=uv_name)

    # get the metadata_dict contained within the uv_file object
    # and combine it with my predefined terms
    metadata_dict.update(uv_file.metadata)
    metadata_dict.update(datadir.metadata)

    uv_data_dict["data"] = uv_data_to_df(uv_file=uv_file)
    uv_data_dict["id"] = metadata_dict["id"]

    # except Exception as e:
    #     logger.error(f"{metadata_dict['path']} encountered an error: {e}")

    returndict: Dict[
        str, Union[Dict[str, str], Dict[str, Union[str, pd.DataFrame]]]
    ] = {
        "metadata": metadata_dict,
        "data": uv_data_dict,
    }

    return returndict
