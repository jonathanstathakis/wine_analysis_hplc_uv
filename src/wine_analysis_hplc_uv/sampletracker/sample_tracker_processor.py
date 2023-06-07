"""
Driver class for sampletracker processes

Initialized with a WorkSheet object that provides a dataframe and sheet_title.

Exporting back to Sheets (if desired) can either use that WorkSheet object or create a new one, if a new `sheet_title` is provided.

2023-06-03 17:29:39
TODO:
- [ ] continue organizing and cleaning SampleTracker class
"""

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st_methods
from wine_analysis_hplc_uv.sampletracker import sample_tracker_cleaner
from wine_analysis_hplc_uv.sampletracker import init_raw_sample_tracker_table
import pandas as pd


class SampleTracker:
    def __init__(self, sheet_title: str, key=st_methods.get_gsheet_key()) -> None:
        assert isinstance(key, str)
        self.sheet_title = sheet_title
        self.key = key
        self.wksh = st_methods.get_sample_tracker_wksh(
            self.key, sheet_title=sheet_title
        )
        self.df: pd.DataFrame = self.sheets_to_df_helper()
        self.tbl_name = "sampletracker"

    def sheets_to_df_helper(self) -> pd.DataFrame:
        """_summary_
        Build the sampletracker df from the Google Sheets table.
        Returns:
            pd.DataFrame: _description_
        """
        df: pd.DataFrame = st_methods.sample_tracker_df_builder(
            sample_tracker_wksh=self.wksh
        )
        return df

    def clean_df_helper(self) -> None:
        self.df: pd.DataFrame = sample_tracker_cleaner.sample_tracker_df_cleaner(
            self.df
        )
        return None

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

    def to_sheets_helper(self, sheet_title: str = None, sudo: bool = False) -> None:
        """_summary_
        Push current clean_df to the google sheets workbook as a new sheet.

        args:
        :param clean_df : use clean_df if True, else df
        :type clean_df : bool
        """
        st_methods.st_to_sheets(sample_tracker=self, sheet_title=sheet_title, sudo=sudo)
