"""
A file to contain all of the necessary cellartracker cleaning functions, to be run once the raw table is downloaded but before other operations. Works in conjuction with prototype_code/init_table_cellartracker.py
"""

import html
import numpy as np
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.generic import Exporter

from wine_analysis_hplc_uv.definitions import (
    DB_PATH,
    CT_TBL_NAME,
    CLEAN_CT_TBL_NAME,
    TEST_SHEETS_KEY,
)


class CTCleaner(Exporter):
    def ct_cleaner(self):
        self.df = df_cleaning_methods.df_string_cleaner(self.df)
        self.df.columns = self.df.columns.str.lower()
        self.df = self.df.rename({"wine": "name"}, axis=1)
        self.df = self.df.replace({"1001": np.nan})

        def unescape_html(s):
            return html.unescape(s)

        try:
            self.df["name"] = self.df["name"].apply(unescape_html)
        except TypeError as e:
            print("Type error encountered when cleaning html characters:", e)

        return self.df

    def __init__(self, db_path: str, raw_tbl_name: str):
        self.db_path = db_path
        self.raw_tbl_name = raw_tbl_name
        self.df = db_methods.tbl_to_df(self.db_path, self.raw_tbl_name)
        self.clean_df = self.ct_cleaner()


def main():
    ct_cleaner = CTCleaner(DB_PATH, CT_TBL_NAME)
    ct_cleaner.to_db(db_filepath=DB_PATH, tbl_name=CLEAN_CT_TBL_NAME)
    ct_cleaner.to_sheets(key=TEST_SHEETS_KEY, sheet_title=CLEAN_CT_TBL_NAME)

    return None


if __name__ == "__main__":
    main()
