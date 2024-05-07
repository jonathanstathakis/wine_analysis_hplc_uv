import pandas as pd
from wine_analysis_hplc_uv.df_methods.df_methods import logger


def test_df(df: pd.DataFrame) -> None:
    logger.info("testing if df empty..")
    assert not df.empty, "DataFrame is empty"
    logger.info("testing for any nulls..")
    assert not df.isnull().values.all(), "DataFrame contains NaN values"
    logger.info("testing for any duplicate rows..")
    assert (
        len(df.drop_duplicates()) > 1
    ), "DataFrame does not have more than one unique row"
    return None
