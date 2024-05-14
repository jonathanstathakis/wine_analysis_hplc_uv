"""
2023-08-21 14:12:15

A module to take the current multiindexed dataframe of shape
[range_idx: (samplecode, wine, vars)] where vars = [mins, value], where
value = absorbance and reshape it into the form appropriate for the peak alignment
pipe constructed back in autumn.
"""

from wine_analysis_hplc_uv.etl.build_library.db_methods import get_data, pivot_wine_data
from wine_analysis_hplc_uv.old_signal_processing.peak_alignment import (
    peak_alignment_pipe,
)
from wine_analysis_hplc_uv import definitions
import duckdb as db
import pandas as pd

pd.options.display.width = None
pd.options.display.max_colwidth = 20
pd.options.display.max_rows = 20
pd.options.display.max_columns = 15
pd.options.display.colheader_justify = "left"


def main():
    wd = get_data.WineData(db_path=definitions.DB_PATH)
    wd.get_wine_data(
        detection=("cuprac",),
        varietal=("pinot noir",),
        wavelength=(450,),
        mins=(0, 5),
    )
    wide_df = pivot_wine_data.pivot_wine_data(wd.con)

    # convert to a dictionary based on samplecode. Do this by iterating thru it i guess
    df_dict = {}
    grouped = wide_df.stack(["samplecode", "wine"]).groupby("samplecode")

    for key, group in grouped:
        df_dict[key] = group[["mins", "value"]]

    df_series = pd.Series(df_dict)
    df = pd.DataFrame()
    df["raw_df"] = df_series
    peak_alignment_pipe.peak_alignment_pipe(df)


if __name__ == "__main__":
    main()
