"""
2023-11-16 08:56:48

2023-11-17 08:57:57

TODO:

- [ ] Get 5 samples for testing
- [ ] test peak profiling on 5 random samples
- [ ] optimize generalized peak profiling by tweaking hyperparameters
- [ ] Write a summary of the methods used by py-hplc
- [ ] run for whole dataset, write to DB. Thus need to make sure that label columns such as ID are joined to peak table
- [ ] begin binning by category. define minimum width as peak width minimum in selected dataset
- [ ] observe binning results of 5 random samples
- [ ] perform ANOVA (or MANOVA) on binned dataset
- [ ] attempt multiclass modeling on binned (aligned) dataset
- [ ] perform PCA on binned dataset
"""

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

import logging

# logger = logging.basicConfig(level="DEBUG")


class HPLCPy(Chromatogram):
    def __init__(self, kwargs):
        Chromatogram.__init__(self, **kwargs)

    def _window_plot(self):
        # Plot each window
        for g, d in self.window_df.groupby("window_id"):
            plt.plot(d["time"], d["signal"], "-", lw=3, label=f" window: {g}")
        plt.xlabel("time [min]")
        plt.ylabel("signal [mV]")

        plt.legend()

        plt.show()

        return None

    def assign_windows_and_plot(self):
        self._assign_windows(prominence=0.01)
        self._window_plot()

    def subtract_baseline_and_plot(self):
        S = self.df["signal"].values
        x = self.df.time

        def apply_lls_operator(S):
            # enhance small peaks while compressing signal across orders of magnitude
            S_LLS = np.log(np.log(np.sqrt(S + 1) + 1) + 1)

            return S_LLS

        def plot_lls(x, S_LLS):
            plt.plot(x, S_LLS, "-", color="r", label="$S_{LLS}$")
            plt.legend()
            plt.xlabel("time")
            plt.ylabel("signal")

            return None

        S_LLS = apply_lls_operator(S)

        plot_lls(x, S_LLS)

        # Define a function to compute the minimum filter
        def min_filt(S_LLS, m):
            """Applies the SNIP minimum filter defined in Eq. 2"""
            S_LLS_filt = np.copy(S_LLS)
            for i in range(m, len(S_LLS) - m):
                S_LLS_filt[i] = min(S_LLS[i], (S_LLS[i - m] + S_LLS[i + m]) / 2)
            return S_LLS_filt

        def plot_its(x, S_LLS):
            # Apply the filter for the first 100 iterations and plot
            S_LLS_filt = np.copy(S_LLS)
            for m in range(200):
                S_LLS_filt = min_filt(S_LLS_filt, m)
                # Plot every ten iterations
                if (m % 20) == 0:
                    plt.plot(x, S_LLS_filt, "-", label=f"iteration {m}", lw=2)

            plt.legend()
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
            plt.xlabel("time")
            plt.ylabel("signal")
            plt.show()
            plt.close()
            return None

        plot_its(x, S_LLS)

        def inverse_tarnsform_range(S_LLS_filt):
            S_prime = (np.exp(np.exp(S_LLS_filt) - 1) - 1) ** 2 - 1
            return S_prime

        S_LLS_filt = min_filt(S_LLS, 70)

        S_prime = inverse_tarnsform_range(S_LLS_filt=S_LLS_filt)

        def baseline_subtract(S, S_prime):
            return S - S_prime

        S_subtracted = baseline_subtract(S, S_prime)

        def plot_subtraction(x, S, S_subtracted):
            plt.plot(x, S, "-", lw=2, label="true signal")
            plt.plot(
                x,
                S_subtracted,
                "-",
                alpha=0.8,
                lw=2,
                color="r",
                label="baseline-subtracted signal",
            )
            plt.legend()
            plt.xlabel("time")
            plt.ylabel("signal")

            plt.show()
            plt.close()

            return None

        plot_subtraction(x, S, S_subtracted)
        # # show chromatogram
        # fig, ax = self.show()

        # # plot true signal
        # ax.plot(self.df.time, self.df.signal_corrected, 'r--', label='true signal')
        # ax.legend()

        # fig.show()

    def windows_with_subtraction(self, window_val):
        self.correct_baseline(window_val)


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

    hplcpy = HPLCPy(chromkwargs)

    # hplcpy.subtract_baseline_and_plot()()

    hplcpy.correct_baseline(window=0.7)

    hplcpy.assign_windows_and_plot()


if __name__ == "__main__":
    main()
