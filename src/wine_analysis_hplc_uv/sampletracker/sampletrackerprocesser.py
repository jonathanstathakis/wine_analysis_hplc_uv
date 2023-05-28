"""
Driver class for sampletracker processes
"""

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st
from wine_analysis_hplc_uv.sampletracker import sample_tracker_cleaner
from wine_analysis_hplc_uv.sampletracker import init_raw_sample_tracker_table
import pandas as pd


class SampleTracker:
    """
    Class to wrap around all pertinant sampletracker methods
    """

    def __init__(self) -> None:
        self.df: pd.DataFrame = self.st_df_helper()
        self.clean_df: pd.DataFrame = self.clean_st()
        self.tbl_name = "sampletracker"

    def st_to_db(self, clean: bool) -> None:
        df: pd.DataFrame = self.st_df_helper()
        if clean:
            self.clean_df.pipe(self.st_to_db)
        else:
            self.df.pipe(self.st_to_db, self.db_filepath)

    def st_df_helper(self) -> pd.DataFrame:
        """_summary_
        Build the sampletracker df from the Google Sheets table.
        Returns:
            pd.DataFrame: _description_
        """
        df: pd.DataFrame = st.sample_tracker_df_builder()
        return df

    def st_to_db_helper(
        self, df: pd.DataFrame, db_filepath: str, db_tbl_name: str
    ) -> None:
        init_raw_sample_tracker_table.sampletracker_to_db(
            df=df, db_filepath=db_filepath, db_table_name=db_tbl_name
        )

    def clean_st(self) -> pd.DataFrame:
        df: pd.DataFrame = sample_tracker_cleaner.sample_tracker_df_cleaner(self.df)
        return df
