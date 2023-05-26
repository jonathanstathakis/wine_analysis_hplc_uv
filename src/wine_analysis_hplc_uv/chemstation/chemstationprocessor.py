import os
import pandas as pd

from wine_analysis_hplc_uv.chemstation import (
    chemstation_methods,
    chemstation_to_db_methods,
    pickle_chemstation_data,
    ch_metadata_tbl_cleaner
)
from typing import List, Tuple


class ChemstationProcessor:
    

    def __init__(self, datalibpath: str):
        assert os.path.isdir(s=datalibpath)
        self.datalibpath: str = datalibpath

        self.pkfname = "chemstation_process_picklejar/chemstation_data_dicts_tuple.pk"

        self.pkfpath: str = os.path.join(datalibpath, self.pkfname)

        self.fpathlist: List[str] = chemstation_methods.uv_filepaths_to_list(
            root_dir_path=datalibpath
        )

        self.ch_data_dicts_tuple: Tuple[
            list[dict], list[dict]
        ] = pickle_chemstation_data.pickle_interface(
            pickle_filepath=self.pkfpath, uv_paths_list=self.fpathlist
        )
        self.metadata_df = chemstation_to_db_methods.metadata_list_to_df(self.ch_data_dicts_tuple[0])

    def to_db(
        self,
        db_filepath: str,
        ch_metadata_tblname: str = "ch_metadata",
        ch_sc_tblname: str = "ch_sc_data",
    ) -> None:
        chemstation_to_db_methods.write_chemstation_to_db(
            ch_tuple=self.ch_data_dicts_tuple,
            db_filepath=db_filepath,
            chemstation_metadata_tblname=ch_metadata_tblname,
            chromatogram_spectrum_tblname=ch_sc_tblname
        )

    def clean_metadata(self) -> pd.DataFrame:
        return ch_metadata_tbl_cleaner.ch_metadata_tbl_cleaner(self.metadata_df)


if __name__ == "__main__":
    chprocess = ChemstationProcessor(
        "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/data/cuprac_data"
    )
    
    chprocess.to_db(db_filepath=(os.path.join(chprocess.datalibpath, 'test.db')))
