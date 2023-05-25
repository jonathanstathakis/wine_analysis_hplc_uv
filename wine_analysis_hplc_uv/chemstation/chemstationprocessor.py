import os

from rainbow.agilent import chemstation

from wine_analysis_hplc_uv.chemstation import (
    chemstation_methods,
    chemstation_to_db_methods,
    pickle_chemstation_data,
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

    def to_db(
        self,
        db_filepath: str,
        ch_metadata_tblname: str = "ch metadata",
        ch_sc_tblname: str = "ch sc data",
    ) -> None:
        chemstation_to_db_methods.write_chemstation_data_to_db_entry(
            chemstation_data_dicts_tuple=self.ch_data_dicts_tuple,
            db_filepath=db_filepath,
            ch_metadata_tblname=ch_metadata_tblname,
            ch_sc_tblname=ch_sc_tblname,
        )


if __name__ == "__main__":
    chprocess = ChemstationProcessor(
        "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/data/cuprac_data"
    )
    
    print(chprocess.ch_data_dicts_tuple[0])
