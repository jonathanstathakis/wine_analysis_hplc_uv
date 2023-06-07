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
    def __init__(self, sheet_title: str, key=st_methods.get_gsheet_key()) -> None:
        assert isinstance(key, str)
        self.key = key
        self.wksh = st_methods.get_sample_tracker_wksh(
            self.key, sheet_title=sheet_title
        )
        self.df: pd.DataFrame = self.sheets_to_df_helper()
        self.clean_df = None
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
        self.clean_df: pd.DataFrame = sample_tracker_cleaner.sample_tracker_df_cleaner(
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

    def to_sheets(
        self, google_api_dict: dict, sheet_title: str, clean_df: bool
    ) -> None:
        """_summary_
        Push current clean_df to the google sheets workbook as a new sheet.

        args:
        :param clean_df : use clean_df if True, else df
        :type clean_df : bool
        """

        assert isinstance(sheet_title, str)
        assert isinstance(google_api_dict, dict)

        if clean_df:
            response, data = st_methods.st_to_sheets(
                self.clean_df, google_api_dict, sheet_title
            )
        else:
            response, data = st_methods.st_to_sheets(
                self.df, google_api_dict, sheet_title
            )
        return response, data

    # def to_sheets(self)-> None:
