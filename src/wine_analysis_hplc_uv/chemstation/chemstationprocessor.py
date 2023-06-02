import os
import pandas as pd
import shutil

from wine_analysis_hplc_uv.chemstation import (
    chemstation_methods,
    chemstation_to_db_methods,
    pickle_chemstation_data,
    ch_metadata_tbl_cleaner,
)
from wine_analysis_hplc_uv.chemstation.process_outputs import output_to_csv
from typing import List, Tuple, Dict


class ChemstationProcessor:
    """
    Chemstation data processor. Make sure to run ChemstationProcessor.cleanup_pickle() at the end to clean up the picklejar and pickle at the end of the process.
    """

    def __init__(self, datalibpath: str, usepickle: bool = False):
        assert os.path.isdir(s=datalibpath)
        self.datalibpath: str = datalibpath

        self.pkfname = "chemstation_process_picklejar/chemstation_data_dicts_tuple.pk"

        self.pkfpath: str = os.path.join(datalibpath, self.pkfname)

        self.fpathlist: List[str] = chemstation_methods.uv_filepaths_to_list(
            root_dir_path=datalibpath
        )

        self.data_dict_tuple: Tuple[
            list[dict], list[dict]
        ] = pickle_chemstation_data.pickle_interface(
            pickle_filepath=self.pkfpath,
            uv_paths_list=self.fpathlist,
            usepickle=usepickle,
        )
        self.metadata_df: pd.DataFrame = chemstation_to_db_methods.metadata_list_to_df(
            self.data_dict_tuple[0]
        )

        self.data_df: pd.DataFrame = data_to_df(self.data_dict_tuple)

        if usepickle:
            self.cleanup_pickle()

    def to_db(
        self,
        db_filepath: str,
        ch_metadata_tblname: str = "ch_metadata",
        ch_sc_tblname: str = "ch_sc_data",
    ) -> None:
        chemstation_to_db_methods.write_chemstation_to_db(
            ch_tuple=self.data_dict_tuple,
            db_filepath=db_filepath,
            chemstation_metadata_tblname=ch_metadata_tblname,
            chromatogram_spectrum_tblname=ch_sc_tblname
        )

    def clean_metadata(self) -> pd.DataFrame:
        return ch_metadata_tbl_cleaner.ch_metadata_tbl_cleaner(self.metadata_df)
    
    def cleanup_pickle(self) -> None:
        assert os.path.exists(self.pkfpath)
        print(f"removing process pickle at {self.pkfpath}..\n")
        shutil.rmtree(os.path.dirname(self.pkfpath))
        print(f"file removed..\n")
        return None
    
    def to_csv_helper(self):
        output_to_csv.data_to_csv(self.data_dict_tuple, self.datalibpath, cleanup=True)


def data_to_df(data_dict_tuple: Tuple) -> pd.DataFrame:
    """
    For a given list of dicts of ch data: {'hash_key':str,'data': pd.DataFrame}, add the hash key as a column of the dataframe and concat all the data in the list into 1 dataframe. Ideal for joins, writing to db without loops.
    """

    def form_data_df(data_dict: Dict) -> pd.DataFrame:
        """
        Form a data df of format: [hash_column, [data_columns]] from the dict.
        """
        data_df: pd.DataFrame = data_dict["data"]
        data_df["hash_key"] = data_dict["hash_key"]

        return data_df

    data_list = data_dict_tuple[1]

    data_hash_df_list = [form_data_df(data_dict) for data_dict in data_list]

    data_df: pd.DataFrame = pd.concat(data_hash_df_list, axis=0, ignore_index=True)

    return data_df


if __name__ == "__main__":
    chprocess = ChemstationProcessor(
        "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/data/cuprac_data"
    )

    chprocess.to_db(db_filepath=(os.path.join(chprocess.pkfpath, "test.db")))
