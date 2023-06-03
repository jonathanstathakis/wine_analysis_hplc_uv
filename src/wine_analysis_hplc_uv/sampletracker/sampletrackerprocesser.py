"""
Driver class for sampletracker processes

2023-06-03 17:29:39
TODO:
- [ ] continue organizing and cleaning SampleTracker class
"""

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st_methods
from wine_analysis_hplc_uv.sampletracker import sample_tracker_cleaner
from wine_analysis_hplc_uv.sampletracker import init_raw_sample_tracker_table
import pandas as pd


class SampleTracker:
    def __init__(self, columns_dict: dict, google_api_dict: dict) -> None:
        self.df: pd.DataFrame = self.st_df_helper(columns_dict, google_api_dict)
        self.clean_df: pd.DataFrame = self.clean_df_helper()
        self.tbl_name = "sampletracker"

    def st_df_helper(self, columns_dict: dict, google_api_dict: dict) -> pd.DataFrame:
        """_summary_
        Build the sampletracker df from the Google Sheets table.
        Returns:
            pd.DataFrame: _description_
        """
        df: pd.DataFrame = st_methods.sample_tracker_df_builder(
            columns_dict, google_api_dict
        )
        return df

    def clean_df_helper(self) -> pd.DataFrame:
        clean_df: pd.DataFrame = sample_tracker_cleaner.sample_tracker_df_cleaner(
            self.df
        )
        return clean_df

    def st_to_db_helper(
        self, df: pd.DataFrame, db_filepath: str, db_tbl_name: str
    ) -> None:
        init_raw_sample_tracker_table.sampletracker_to_db(
            df=df, db_filepath=db_filepath, db_table_name=db_tbl_name
        )

    def st_to_db(self, clean: bool, db_filepath: str) -> None:
        if clean:
            self.clean_df.pipe(self.st_to_db)
        else:
            self.df.pipe(self.st_to_db, db_filepath)
        return None

    # def to_sheets(self)-> None:
