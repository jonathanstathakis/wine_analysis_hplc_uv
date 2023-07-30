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
    def clean_st(self, df):
        """
        apply df_string_cleaner, strips and lowers column, index and values of the passed dataframe.
        """

        self.df = df_cleaning_methods.df_string_cleaner(df)

        return self.df
