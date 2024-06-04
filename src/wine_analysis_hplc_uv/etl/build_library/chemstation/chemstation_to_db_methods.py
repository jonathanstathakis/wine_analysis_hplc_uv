"""
A module to db_filepathtain chemstation database interface methods
"""

import pandas as pd
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
