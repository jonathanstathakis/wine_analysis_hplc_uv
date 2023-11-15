from wine_analysis_hplc_uv import definitions

import pandas as pd
import numpy as np

from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract

de = dataextract.DataExtractor(db_path=definitions.DB_PATH)

de.create_subset_table(detection=("cuprac",), mins=(0, 1))
df = de.get_tbl_as_df()

unique_df = df.drop_duplicates("id", keep="first")

print(unique_df.head())
print(unique_df.color.value_counts())

# for each color, get the size of classes
print(unique_df.groupby(["color", "varietal"]).size().sort_values(ascending=False))

"""
red     pinot noir            8
        shiraz                7
white   chardonnay            6
"""

color_df = (
    df.set_index(["detection", "color"])
    .loc[:, "code_wine"]
    .drop_duplicates()
    .groupby(["detection", "color"])
    .size()
)

print(color_df.head())
