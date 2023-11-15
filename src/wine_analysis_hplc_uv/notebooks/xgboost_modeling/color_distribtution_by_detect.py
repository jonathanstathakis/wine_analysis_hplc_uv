from wine_analysis_hplc_uv import definitions

import pandas as pd
import numpy as np

from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract

de = dataextract.DataExtractor(db_path=definitions.DB_PATH)

de.create_subset_table(mins=(0, 1))
df = de.get_tbl_as_df()

print(
    df.drop_duplicates("id")
    .groupby(["detection", "color"])
    .size()
    .to_frame("n")
    .reset_index()
    .sort_values(["detection", "n"], ascending=False)
    .pivot_table(
        index="color",
        columns="detection",
        values="n",
        fill_value=0,
        margins=True,
        aggfunc="sum",
    )
    .assign(sortkey=lambda df: df.index == "All")
    .sort_values(["sortkey", "All"], ascending=[True, False])
    .drop("sortkey", axis=1)
)

color_df = (
    df.set_index(["detection", "color"])
    .loc[:, "code_wine"]
    .drop_duplicates()
    .groupby(["detection", "color"])
    .size()
)

# print(color_df.head())
