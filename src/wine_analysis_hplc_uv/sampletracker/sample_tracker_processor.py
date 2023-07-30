"""
Driver class for sampletracker processes

Initialized with a WorkSheet object that provides a dataframe and sheet_title.

Exporting back to Sheets (if desired) can either use that WorkSheet object or create a new one, if a new `sheet_title` is provided.
"""

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st_methods
import pandas as pd
from wine_analysis_hplc_uv.generic import Exporter


class SampleTracker(Exporter):
    def __init__(self, sheet_title: str, key=st_methods.get_gsheet_key()) -> None:
        assert isinstance(key, str)
        self.sheet_title = sheet_title
        self.key = key
        self.wksh = st_methods.get_sample_tracker_wksh(
            self.key, sheet_title=sheet_title
        )
        self.df = self.wksh.sheet_df

    # def to_db(self, db_filepath: str, db_tbl_name: str) -> None:
    #     init_raw_sample_tracker_table.sampletracker_to_db(
    #         df=self.df, db_filepath=db_filepath, db_table_name=db_tbl_name
    #     )

    def to_sheets_helper(self, sheet_title: str = None, sudo: bool = False) -> None:
        """_summary_
        Push current clean_df to the google sheets workbook as a new sheet.

        args:
        :param clean_df : use clean_df if True, else df
        :type clean_df : bool
        """
        st_methods.st_to_sheets(sample_tracker=self, sheet_title=sheet_title, sudo=sudo)
