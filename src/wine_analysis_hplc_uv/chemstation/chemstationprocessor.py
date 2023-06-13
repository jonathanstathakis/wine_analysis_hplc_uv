from multiprocessing import process
import os
import pandas as pd
import shutil

from wine_analysis_hplc_uv.chemstation import logger

from wine_analysis_hplc_uv.chemstation import (
    chemstation_methods,
    chemstation_to_db_methods as ch_db,
    ch_data_multiprocess,
    ch_metadata_tbl_cleaner as ch_m_clean,
)
from wine_analysis_hplc_uv.chemstation.process_outputs import output_to_csv
from typing import List, Tuple, Dict


class ChemstationProcessor:
    """
    # Chemstation data processor.
    Make sure to run ChemstationProcessor.cleanup_pickle() at the end
    to clean up the picklejar and pickle at the end of the process.

    Members:
    datalibpath
    pkfname
    pkfpath
    fpathlist
    data_dict_tuple
    metadata_df
    data_df
    to_db()
    clean_metadata()
    cleanup_pickle()
    to_csv()
    """

    def __init__(self, datalibpath: str, usepickle: bool = False):
        assert os.path.isdir(s=datalibpath)
        self.datalibpath: str = datalibpath

        self.pkfname = "chemstation_process_picklejar/chemstation_data_dicts_tuple.pk"
        self.pkfpath: str = os.path.join(datalibpath, self.pkfname)

        self.fpathlist: List[str] = chemstation_methods.uv_filepaths_to_list(
            root_dir_path=datalibpath
        )

        self.metadata_df, self.data_df = ch_data_multiprocess.ch_data_multiprocess(
            self.fpathlist
        )

    def to_db(
        self,
        db_filepath: str,
        ch_metadata_tblname: str = "ch_metadata",
        ch_sc_tblname: str = "ch_sc_data",
    ) -> None:
        ch_db.write_chemstation_to_db(
            ch_tuple=self.data_dict_tuple,
            db_filepath=db_filepath,
            chemstation_metadata_tblname=ch_metadata_tblname,
            chromatogram_spectrum_tblname=ch_sc_tblname,
        )

    def clean_metadata(self) -> pd.DataFrame:
        return ch_m_clean.ch_metadata_tbl_cleaner(self.metadata_df)

    def cleanup_pickle(self) -> None:
        assert os.path.exists(self.pkfpath)
        logger.debug(f"removing process pickle at {self.pkfpath}..\n")
        shutil.rmtree(os.path.dirname(self.pkfpath))
        logger.debug("file removed..\n")
        return None

    def to_csv_helper(
        self,
        wavelengths: List[str] = ["*"],
        cleanup: bool = True,
        forceoverwrite: bool = False,
    ) -> None:
        output_to_csv.chprocess_to_csv(
            metadata_df=self.metadata_df,
            data_df=self.data_df,
            data_lib_path=self.datalibpath,
            wavelengths=wavelengths,
            cleanup=cleanup,
            forceoverwrite=forceoverwrite,
        )

        return None


if __name__ == "__main__":
    chprocess = ChemstationProcessor(
        "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/data/cuprac_data"
    )

    chprocess.to_db(db_filepath=(os.path.join(chprocess.pkfpath, "test.db")))
