"""
A module to db_filepathtain chemstation database interface methods
"""
from typing import Tuple, List, Dict
import pandas as pd
from wine_analysis_hplc_uv.db_methods import db_methods
import logging

logger = logging.getLogger(__name__)


def write_chemstation_to_db(
    self, ch_m_tblname: str, ch_sc_tblname: str, con: str
) -> None:
    # write metadata table, chromatogram_spectra table.

    self.metadata_df.pipe(df_to_db, con=con, tblname=ch_m_tblname)
    self.data_df.pipe(df_to_db, con=con, tblname=ch_sc_tblname)


def df_to_db(df: pd.DataFrame, tblname: str, con: str) -> None:
    logger.info(f"writing df to {tblname} table..")
    try:
        con.sql(
            f"""
                CREATE OR REPLACE TABLE
                {tblname}
                AS
                SELECT * FROM df
                """
        )
        assert not con.sql(f"SELECT * FROM {tblname}").df().empty
    except Exception as e:
        logger.error(e)
        logger.error(tblname)
    return None
