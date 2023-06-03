"""
Driver class for sampletracker processes
"""

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st
from wine_analysis_hplc_uv.sampletracker import sample_tracker_cleaner as st_cleaner
from wine_analysis_hplc_uv.sampletracker import init_raw_sample_tracker_table as raw_st
import pandas as pd


class SampleTracker:
    def __init__(self, db_filepath: str) -> None:
        self.db_filepath = db_filepath
        self.df: pd.DataFrame = self.st_to_df()
        # self.clean_df: pd.DataFrame = self.clean_st(self.db_filepath, "test")

    def st_to_df(self) -> pd.DataFrame:
        df: pd.DataFrame = st.sample_tracker_df_builder()
        return df

    def st_to_db(self, df: pd.DataFrame, db_filepath: str, db_tbl_name: str) -> None:
        raw_st.sampletracker_to_db(
            df=df, db_filepath=db_filepath, db_table_name=db_tbl_name
        )

    def clean_st(self, db_filepath: str, tbl_name: str) -> None:
        st_cleaner.clean_sample_tracker_table(db_filepath, tbl_name)
        return None
