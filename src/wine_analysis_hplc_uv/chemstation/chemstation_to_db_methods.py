"""
A module to db_filepathtain chemstation database interface methods
"""
from typing import Tuple, List, Dict
import pandas as pd
from wine_analysis_hplc_uv.db_methods import db_methods


def write_chemstation_to_db(
    self,
    chemstation_metadata_tblname: str,
    chromatogram_spectrum_tblname: str,
    db_filepath: str,
) -> None:
    # write metadata table, chromatogram_spectra table.

    metadata_df_to_db(
        metadata_df=self.metadata_df,
        tblname=chemstation_metadata_tblname,
        db_filepath=db_filepath,
    )
    data_df_to_db(
        data_df=self.data_df,
        tblname=chromatogram_spectrum_tblname,
        db_filepath=db_filepath,
    )
    return None


def metadata_df_to_db(metadata_df: pd.DataFrame, tblname: str, db_filepath: str):
    metadata_df.pipe(db_methods.df_to_tbl, tblname, db_filepath)
    return None


def data_df_to_db(data_df: pd.DataFrame, tblname: str, db_filepath: str) -> None:
    data_df.pipe(db_methods.df_to_tbl, tblname, db_filepath)
    return None
