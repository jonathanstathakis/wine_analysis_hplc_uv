import pandas as pd
from wine_analysis_hplc_uv.chemstation.ch_m_cleaner import ch_m_samplecode_cleaner
from wine_analysis_hplc_uv.chemstation.ch_m_cleaner import ch_m_date_cleaner
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.generic import Exporter


class ChemstationCleaner(Exporter):
    def c_ch_m_to_db(db_path, raw_tbl_name, clean_tbl_name):
        """
        1. Get the raw table as a df
        2. clean the df
        3. write the df to db
        """
        dirty_df = db_methods.tbl_to_df(db_filepath=db_path, tblname=raw_tbl_name)
        # clean_df = ch_metadata_tbl_cleaner(df = dirty_df)
        # db_methods.df_to_tbl(df=clean_df, tblname=clean_tbl_name, db_filepath=db_path)
        return None

    def ch_metadata_tbl_cleaner(df: pd.DataFrame) -> pd.DataFrame:
        """
        driver function for cleaning chemstation metadata table to enable joins with sample_tracker table
        """

        df = (
            df.pipe(df_cleaning_methods.df_string_cleaner)
            .pipe(rename_chemstation_metadata_cols)
            .pipe(ch_m_date_cleaner.format_acq_date())
            .pipe(ch_m_samplecode_cleaner.ch_m_samplecode_cleaner)
            # .pipe(chemstation_metadata_drop_unwanted_runs)
        )

        return df

    def rename_chemstation_metadata_cols(df):
        original_names = ["notebook", "date", "method"]
        new_names = ["samplecode", "acq_date", "acq_method"]

        rename_dict = dict(zip(original_names, new_names))
        df = df.rename(rename_dict, axis=1)
        assert not df.columns.isin(original_names).all()
        assert df.columns.isin(new_names).any()
        return df


def main():
    return None


if __name__ == "__main__":
    main()
