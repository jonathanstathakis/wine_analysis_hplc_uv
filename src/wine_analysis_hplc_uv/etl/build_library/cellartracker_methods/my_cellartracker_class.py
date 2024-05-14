"""
A cellartracker class inheriting from CellarTracker with cleaning and export functionality
"""
from cellartracker import cellartracker
import pandas as pd
from wine_analysis_hplc_uv.etl.build_library.generic import Exporter


class MyCellarTracker(cellartracker.CellarTracker, Exporter):
    def __init__(self, username: str, password: str) -> None:
        cellartracker.CellarTracker.__init__(self, username=username, password=password)
        Exporter.__init__(self)
        df = pd.DataFrame(self.get_list())

        usecols = [
            "Size",
            "Vintage",
            "Wine",
            "Locale",
            "Country",
            "Region",
            "SubRegion",
            "Appellation",
            "Producer",
            "Type",
            "Color",
            "Category",
            "Varietal",
        ]
        self.df: pd.DataFrame = df[usecols]
