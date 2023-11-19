from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.signal_analysis import signal_analysis
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import testdata

from scipy import signal
import pandas as pd
import seaborn.objects as so
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt


class PeakPlotter(signal_analysis.SignalAnalyzer):
    def __init__(
        self,
        data: pd.DataFrame,
        grouper: str | list,
        target_col: str,
        peak_finder_kws: dict = dict(),
    ):
        self.data = data
        self.grouper = grouper
        self.target_col = target_col
        self.peak_finder_kws = peak_finder_kws
        self.normsig = "scaledsig"

        self.minmaxscaler = None

        self.scale_data()

    def scale_data(self):
        self.minmaxscaler = preprocessing.MinMaxScaler()

        base_signal_series = self.data.loc[:, self.target_col]

        signal_vals = base_signal_series.values.reshape(-1, 1)

        minmax_signal = self.minmaxscaler.fit_transform(signal_vals)

        scaled_signal_series = pd.Series(
            minmax_signal.reshape(-1), index=base_signal_series.index, name=self.normsig
        )

        self.data = self.data.assign(**{self.normsig: scaled_signal_series})

    def _create_plot(self):
        prom_ratio = 0.02
        peak_idx, peak_props = signal.find_peaks(
            self.data.loc[:, self.normsig],
            prominence=prom_ratio,
        )

        self.data = self.data.assign(peaks=lambda df: df.loc[peak_idx, self.normsig])

        fig, ax = plt.subplots(1)

        text = f"$N_p$={self.data.peaks.dropna().count()}"
        ax.text(700, 0.8, text, ha="right", va="top")

        (
            so.Plot(self.data.reset_index(), x="index", y=self.normsig)
            .add(so.Line())
            .add(so.Dot(color="red", marker="x"), x="index", y="peaks")
            .on(ax)
            .show()
        )

        fig.show()

    def peak_plot(self):
        self._create_plot()


def main():
    db_path = definitions.DB_PATH
    data = (
        testdata.TestData(db_path=db_path)
        .pro_data_.melt(value_name="signal", ignore_index=False)
        .reset_index()
    )

    singlesample = data.groupby("code_wine").get_group(data.code_wine.iloc[0])

    pp = PeakPlotter(singlesample, "code_wine", "signal")

    pp.peak_plot()


if __name__ == "__main__":
    main()
