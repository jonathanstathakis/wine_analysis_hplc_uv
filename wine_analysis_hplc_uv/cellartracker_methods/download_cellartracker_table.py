"""
"""
from ..devtools import project_settings
from cellartracker import cellartracker
import pandas as pd


def get_cellar_tracker_table():
    client = cellartracker.CellarTracker("OctaneOolong", "S74rg4z3r1")

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

    cellar_tracker_df = pd.DataFrame(client.get_list())
    cellar_tracker_df = cellar_tracker_df[usecols]

    # clean it up. lower values and columns, replace 1001 with nv, check datatypes

    return cellar_tracker_df


def main():
    return None


if __name__ == "__main__":
    main()
