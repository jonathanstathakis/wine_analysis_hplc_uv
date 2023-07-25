import html
import numpy as np
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.generic import Exporter
import numpy as np
import pandas as pd


class CTCleaner(Exporter):
    """
    Contains all cleaning cellar tracker methods and inherits export methods from Exporter.
    """

    def lower_cols(self, df):
        return df.rename(columns=str.lower)

    def rename_wine_col(self, df):
        return df.rename({"wine": "name"}, axis=1)

    def replace_vintage_code(self, df):
        return df.replace({"1001": np.nan})

    def unescape_name_html(self, df):
        return df.assign(name=lambda df: df["name"].apply(html.unescape))

    def clean_df(self, df: pd.DataFrame):
        self.df = (
            self.df.pipe(df_cleaning_methods.df_string_cleaner)
            .pipe(self.lower_cols)
            .pipe(self.rename_wine_col)
            .pipe(self.replace_vintage_code)
            .pipe(self.unescape_name_html)
        )
        return self.df
