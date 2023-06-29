from wine_analysis_hplc_uv.generic import Exporter
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.definitions import (
    DB_PATH,
    ST_TBL_NAME,
    CLEAN_ST_TBL_NAME,
    TEST_SHEETS_KEY,
)


class STCleaner(Exporter):
    def st_cleaner(self):
        """
        apply df_string_cleaner, strips and lowers column, index and values of the passed dataframe.
        """

        self.df = df_cleaning_methods.df_string_cleaner(self.df)

        return self.df

    def __init__(self, db_path: str, raw_tbl_name: str):
        self.db_path = db_path
        self.raw_tbl_name = raw_tbl_name
        self.df = db_methods.tbl_to_df(self.db_path, self.raw_tbl_name)
        self.clean_df = self.st_cleaner()


def main():
    st_cleaner = STCleaner(DB_PATH, ST_TBL_NAME)
    st_cleaner.to_db(db_filepath=DB_PATH, tbl_name=CLEAN_ST_TBL_NAME)
    st_cleaner.to_sheets(key=TEST_SHEETS_KEY, sheet_title=CLEAN_ST_TBL_NAME)

    return None


if __name__ == "__main__":
    main()
