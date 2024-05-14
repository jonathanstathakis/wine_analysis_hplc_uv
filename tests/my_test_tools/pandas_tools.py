"""
contains 'verify_df' function to test common expectations of pandas dataframes
"""

import logging
import pandas as pd


logger = logging.getLogger(__name__)


def verify_df(df: pd.DataFrame) -> None:
    """
    test the following:

    1. not empty
    2. no null values
    3. no duplicate rows
    """
    logger.info("testing if df empty..")
    assert not df.empty, "DataFrame is empty"
    logger.info("testing for any nulls..")
    assert not df.isnull().values.all(), "DataFrame contains NaN values"
    logger.info("testing for any duplicate rows..")
    assert (
        len(df.drop_duplicates()) > 1
    ), "DataFrame does not have more than one unique row"
