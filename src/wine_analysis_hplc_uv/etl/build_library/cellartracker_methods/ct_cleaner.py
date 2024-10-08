import html
import numpy as np
from wine_analysis_hplc_uv.etl.build_library import df_cleaning_methods
from wine_analysis_hplc_uv.etl.build_library.generic import Exporter


class CTCleaner(Exporter):
    """
    Contains all cleaning cellar tracker methods and inherits export methods from Exporter.
    """

    def clean_df(self, df):
        self.df = (
            df.pipe(df_cleaning_methods.df_string_cleaner)
            .pipe(self.lower_collabels)
            .pipe(self.rename_wine_col)
            .pipe(self.replace_vintage_code)
            .pipe(self.unescape_name_html)
            .pipe(self.remove_illegal_chars)
            .pipe(self.add_wine_col)
        )

    def lower_collabels(self, df):
        return df.rename(columns=str.lower)

    def rename_wine_col(self, df):
        return df.rename({"wine": "name"}, axis=1)

    def replace_vintage_code(self, df):
        return df.replace({"1001": np.nan})

    def unescape_name_html(self, df):
        return df.assign(name=lambda df: df["name"].apply(html.unescape))

    def remove_illegal_chars(self, df):
        # remove single quote character from df as it causes errors in sql statements during injections
        return df.apply(lambda x: x.replace("'", "", regex=True))

    def add_wine_col(self, df):
        return df.assign(wine=df.vintage + " " + df.name)
