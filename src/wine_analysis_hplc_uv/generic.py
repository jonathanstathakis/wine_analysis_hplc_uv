"""
Generic Class and method definitions
"""
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.my_sheetsinterface import gspread_methods as g_methods
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class Exporter:
    """
    A class to contain df -> sheets and db methods.
    """

    def __init__(self):
        self.df = None

    def to_sheets(self, key: str, sheet_title: str):
        """
        Output the self.df to a given google sheets sheet for a provided key and
        sheet_title. If the sheet doesnt exist in the Sheet, it will be created.
        """
        assert isinstance(key, str)
        assert isinstance(sheet_title, str)
        self.sheets_key = key
        wksh = g_methods.WorkSheet(key=key, sheet_title=sheet_title)
        wksh.sheet_df = self.df
        wksh.write_to_sheet()

    def to_db(self, con, tbl_name: str):
        """
        Output contained self.df to designated database given by filepath.
        """
        db_methods.write_df_to_db(df=self.df, con=con, tblname=tbl_name)
