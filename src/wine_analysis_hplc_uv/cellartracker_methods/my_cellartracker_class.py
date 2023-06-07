"""
A cellartracker class inheriting from CellarTracker with cleaning and export functionality
"""
from cellartracker import cellartracker
import pandas as pd
from wine_analysis_hplc_uv.my_sheetsinterface import gspread_methods as g_methods
import duckdb as db
from wine_analysis_hplc_uv.db_methods import db_methods


class MyCellarTracker(cellartracker.CellarTracker):
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username=username, password=password)
        self.df: pd.DataFrame = pd.DataFrame(self.get_list())


class Exporter:
    """
    A class to contain df -> sheets and db methods.
    """

    def __init__(self):
        self.df = None

    def to_sheets(self, key: str, sheet_title: str):
        """
        Output the self.df to a given google sheets sheet for a provided key and sheet_title. If the sheet doesnt exist in the Sheet, it will be created.
        """
        assert isinstance(key, str)
        assert isinstance(sheet_title, str)
        self.sheets_key = key
        wksh = g_methods.WorkSheet(key=key, sheet_title=sheet_title)
        wksh.sheet_df = self.df
        wksh.write_to_sheet()

    def to_db(self, db_filepath: str, tbl_name: str):
        """
        Output contained self.df to designated database given by filepath.
        """
        df = self.df

        with db.connect(database=db_filepath) as con:
            con.sql(query=f"CREATE TABLE {tbl_name} AS SELECT * FROM df")
