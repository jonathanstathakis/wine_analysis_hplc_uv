from wine_analysis_hplc_uv.notebooks.xgboost_modeling import datasets
from wine_analysis_hplc_uv import definitions
import matplotlib.pyplot as plt

# plt.rcParams['figure.figsize'] = [10,15]
# plt.rcParams['figure.dpi'] = 140


import numpy as np
import seaborn.objects as so
import pandas as pd
from hplc_py.quant import Chromatogram
from wine_analysis_hplc_uv.notebooks.peak_deconv import testdata

from wine_analysis_hplc_uv.notebooks.peak_deconv import peak_deconv


def search_for_windows(df, window_list: list):
    """
    search_for_windows iterate through a list of windows, constructing a facet plot

    _extended_summary_
    """

    def form_concat_df(df, windows_list):
        df.insert(0, "version", "original")

        df_list = [df]

        for num_windows in windows_list:
            chm = Chromatogram(df)

            corrected_df = chm.correct_baseline(num_windows, return_df=True).copy()

            corrected_df["version"] = num_windows

            df_list.append(corrected_df)

            del chm

        concat_df = pd.concat(df_list, axis=0).reset_index(drop=True)

        print(concat_df)

        return concat_df

    def plot_windows(concat_df: pd.DataFrame) -> None:
        (
            so.Plot(concat_df)
            .add(so.Line(), x="time", y="signal")
            .add(so.Line(color="red", alpha=0.5), x="time", y="signal_corrected")
            .facet(col="version", wrap=2)
            .layout(size=(15, 10))
            .show()
        )

        (
            so.Plot(concat_df.query("time<5"), x="time")
            .add(so.Line(), y="signal")
            .add(so.Line(color="red", alpha=0.5), x="time", y="signal_corrected")
            .facet(col="version", wrap=2)
            .layout(size=(15, 10))
            .show()
        )

        return None

    concat_df = form_concat_df(df=df, windows_list=window_list)

    plot_windows(concat_df)

    return None


def main():
    db_path = definitions.DB_PATH
    # data = datasets.RawRedVarietalData(db_path)._pro_data
    td = testdata.TestData(db_path=db_path)

    rs_kwargs = dict(key="code_wine", x=1)

    dset = "pro"
    # dset='raw'

    if dset == "pro":
        pro_df = td.get_processed_samples(rs_kwargs)

        file = pro_df

        chromkwargs = dict(
            file=file,
        )

    else:
        raw_df = td.get_raw_samples("code_wine", 1)
        file = raw_df

        chromkwargs = dict(
            file=file,
        )

    search_for_windows(file, window_list=[0.5, 0.7, 1])


if __name__ == "__main__":
    main()
