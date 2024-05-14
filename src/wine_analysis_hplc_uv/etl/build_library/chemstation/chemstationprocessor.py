import os
import pandas as pd
import collections
from wine_analysis_hplc_uv.etl.build_library.chemstation import (
    chemstation_methods,
    chemstation_to_db_methods as ch_db,
    uv_extractor_pool,
    ch_m_cleaner as ch_m_clean,
)
from wine_analysis_hplc_uv.etl.build_library.chemstation.process_outputs import (
    output_to_csv,
)
from typing import List
import logging

logger = logging.getLogger(__name__)


class ChemstationProcessor:
    """
    Chemstation data processor

    TODO: docstring
    TODO: add datatype specification to metadata df. Is currently all 'object' dtype
    """

    def __init__(self, lib_path: str):
        logger.info("initializing ChemstationProcessor..")
        self.lib_path: str = lib_path

        self.path_list: List[str] = chemstation_methods.uv_filepaths_to_list(
            root_dir_path=lib_path
        )

        self.metadata_df, self.data_df = uv_extractor_pool.uv_extractor_pool(
            dirpaths=self.path_list
        )

        test_dup_ids(self.metadata_df)

    def to_db(
        self,
        con: str,
        ch_metadata_tblname: str = "ch_metadata",
        ch_sc_tblname: str = "ch_sc_data",
    ) -> None:
        ch_db.write_chemstation_to_db(
            self=self,
            con=con,
            ch_m_tblname=ch_metadata_tblname,
            ch_sc_tblname=ch_sc_tblname,
        )

    def clean_metadata(self) -> pd.DataFrame:
        return ch_m_clean.ChMCleaner().clean_ch_m(self.metadata_df)

    def to_csv_helper(
        self,
        wavelengths: List[str] = ["*"],
        cleanup: bool = True,
        forceoverwrite: bool = False,
    ) -> None:
        output_to_csv.chprocess_to_csv(
            metadata_df=self.metadata_df,
            data_df=self.data_df,
            data_lib_path=self.lib_path,
            wavelengths=wavelengths,
            cleanup=cleanup,
            forceoverwrite=forceoverwrite,
        )

        return None


def test_dup_ids(metadata_df: List[dict]) -> None:
    # observe how many unique ids were generated.
    # duplicates are probably caused by duplicate files/filenames.
    logger.debug(f"size of metadata_list: {len(metadata_df)}")

    # print the UUIDs that occur more than once.
    list_of_keys: List[str] = metadata_df["id"].tolist()

    uuid_counts = collections.Counter(list_of_keys)

    duplicates: List[str] = [uuid for uuid, count in uuid_counts.items() if count > 1]

    if duplicates:
        logger.error(f"Duplicate UUIDs: {len(duplicates)}")

        for uuid in duplicates:
            logger.error(f"duplicate id: {uuid}")
            for idx, metadata_row in metadata_df.iterrows():
                if uuid == metadata_row["id"]:
                    logger.error(f"duplicate UUID generated by: {metadata_row['path']}")
    return duplicates


if __name__ == "__main__":
    chprocess = ChemstationProcessor(
        "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/data/cuprac_data"
    )

    chprocess.to_db(con=(os.path.join(chprocess.pkfpath, "test.db")))
