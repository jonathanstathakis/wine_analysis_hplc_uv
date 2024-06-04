from wine_analysis_hplc_uv.etl.build_library.generic import Exporter
from wine_analysis_hplc_uv.etl.build_library import df_cleaning_methods

import logging

logger = logging.getLogger(__name__)


class STCleaner(Exporter):
    def clean_st(self, df):
        """
        apply df_string_cleaner, strips and lowers column, index and values of the passed dataframe.
        """
        logger.info("Cleaning sample_tracker")
        self.df = df_cleaning_methods.df_string_cleaner(df).assign(
            wine=lambda df: df["vintage"] + " " + df["name"]
        )

        return self.df
