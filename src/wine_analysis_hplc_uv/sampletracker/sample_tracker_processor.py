"""
Driver class for sampletracker processes

Initialized with a WorkSheet object that provides a dataframe and sheet_title.

Exporting back to Sheets (if desired) can either use that WorkSheet object or create a new one, if a new `sheet_title` is provided.
"""
from wine_analysis_hplc_uv.generic import Exporter
import logging
from wine_analysis_hplc_uv.my_sheetsinterface.gspread_methods import WorkSheet
import os

logger = logging.getLogger(__name__)


def get_gsheet_key(envar: str = "SAMPLETRACKER_KEY"):
    return os.environ.get(envar)


class SampleTracker(Exporter):
    def __init__(self, sheet_title: str, key=get_gsheet_key()) -> None:
        logger.info("initializing SampleTracker..")
        assert isinstance(key, str)
        self.sheet_title = sheet_title
        self.key = key
        self.wksh = get_sample_tracker_wksh(self.key, sheet_title=sheet_title)
        self.df = self.wksh.sheet_df

    def to_sheets_helper(self, sheet_title: str = None, sudo: bool = False) -> None:
        """_summary_
        Push current clean_df to the google sheets workbook as a new sheet.

        args:
        :param clean_df : use clean_df if True, else df
        :type clean_df : bool
        """
        st_to_sheets(sample_tracker=self, sheet_title=sheet_title, sudo=sudo)


def get_sample_tracker_wksh(key: str, sheet_title: str):
    logger.info(f"getting {sheet_title} worksheet..")
    assert isinstance(key, str)
    wksh = WorkSheet(key=key, sheet_title=sheet_title)
    return wksh


def st_to_sheets(sample_tracker, sheet_title: str, sudo: bool = False):
    """
    Output df contained in SampleTracker class to google sheets at provided spreadsheet. If no sheet_title is provided, will output to the source sheet, but provide a warning
    """
    key = sample_tracker.wksh.key
    if sudo:
        sheet_title = sample_tracker.sheet_title
        sample_tracker.wksh.sheet_df = sample_tracker.df
        sample_tracker.wksh.write_to_sheet()

    elif sheet_title is None:
        if input(f"no sheet_title provided, write to {sheet_title}? (y/n) ") == "y":
            sheet_title = sample_tracker.sheet_title
            sample_tracker.wksh.sheet_df = sample_tracker.df
            sample_tracker.wksh.write_to_sheet()
        else:
            print("bad input, exiting..\n")
            assert ValueError
    else:
        new_wksh = WorkSheet(key, sheet_title=sheet_title)
        new_wksh.sheet_df = sample_tracker.df
        new_wksh.write_to_sheet()
