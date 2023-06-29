import pandas as pd
from wine_analysis_hplc_uv.chemstation.ch_m_cleaner import ch_m_samplecode_cleaner
from wine_analysis_hplc_uv.chemstation.ch_m_cleaner import ch_m_date_cleaner
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.generic import Exporter
from wine_analysis_hplc_uv.definitions import (
    DB_PATH,
    CH_META_TBL_NAME,
    CLEAN_CH_META_TBL_NAME,
)


class ChemstationCleaner(Exporter):
    def ch_metadata_tbl_cleaner(self) -> pd.DataFrame:
        """
        driver function for cleaning chemstation metadata table to enable joins with sample_tracker table
        """

        self.df = (
            self.df.pipe(df_cleaning_methods.df_string_cleaner)
            .pipe(rename_chemstation_metadata_cols)
            .pipe(ch_m_date_cleaner.format_acq_date)
            .pipe(ch_m_samplecode_cleaner.ch_m_samplecode_cleaner)
            # .pipe(chemstation_metadata_drop_unwanted_runs)
        )

        return self.df

    def __init__(self, db_path: str, raw_tbl_name: str):
        self.db_path = db_path
        self.raw_tbl_name = raw_tbl_name

        self.df = db_methods.tbl_to_df(self.db_path, self.raw_tbl_name)
        self.clean_df = self.ch_metadata_tbl_cleaner()


def rename_chemstation_metadata_cols(df):
    """ """
    original_names = ["notebook", "date", "method"]
    new_names = ["samplecode", "acq_date", "acq_method"]

    rename_dict = dict(zip(original_names, new_names))
    df = df.rename(rename_dict, axis=1)
    assert not df.columns.isin(original_names).all()
    assert df.columns.isin(new_names).any()
    return df


def main():
    ch_cleaner = ChemstationCleaner(DB_PATH, CH_META_TBL_NAME)
    ch_cleaner.to_db(db_filepath=DB_PATH, tbl_name=CLEAN_CH_META_TBL_NAME)

    return None


if __name__ == "__main__":
    main()
