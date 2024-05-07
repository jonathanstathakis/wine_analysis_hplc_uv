from wine_analysis_hplc_uv import definitions
import matplotlib.pyplot as plt

# plt.rcParams['figure.figsize'] = [10,15]
# plt.rcParams['figure.dpi'] = 140


import numpy as np
import seaborn.objects as so
import pandas as pd
from hplc_py.quant import Chromatogram
from wine_analysis_hplc_uv.notebooks.peak_deconv import testdata
from scipy import signal

# import seaborn as sns

import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


def fine_tune_window_val(chm: Chromatogram):
    chm.show()

    chm.correct_baseline(window=0.7)

    chm.show()

    chm._assign_windows()

    so.Plot(
        chm.window_df.assign(window_id=lambda df: df.window_id.astype(str)),
        color="window_id",
        x="time",
        y="signal_corrected",
    ).add(so.Line()).show()

    so.Plot(
        chm.window_df.assign(window_id=lambda df: df.window_id.astype(str)).query(
            "(time>=0) & (time<=5)"
        ),
        color="window_id",
        x="time",
        y="signal_corrected",
    ).add(so.Line()).show()

    display(chm.window_df.query("window_id==2").describe())

    so.Plot(
        chm.window_df.assign(window_id=lambda df: df.window_id.astype(str)).query(
            "(time>=19) & (time<=25)"
        ),
        color="window_id",
        x="time",
        y="signal_corrected",
    ).add(so.Line()).show()


def signal_bin_plot(df: pd.DataFrame) -> None:
    num_bins = 5

    df = df.assign(
        time_bins=pd.cut(df.time, bins=num_bins, labels=range(1, num_bins + 1))
    )

    sns.relplot(
        data=df.assign(window_idx_type=lambda x: x.window_id + "_" + x.window_type),
        x="time",
        y="signal_corrected",
        hue="window_idx_type",
        col="time_bins",
        col_wrap=2,
        markers=False,
        kind="line",
        facet_kws={"sharey": False, "sharex": False},
        palette=sns.color_palette(),
    )

    plt.show()

    return None


def estimate_peak_widths(df: pd.DataFrame) -> None:
    # what does find_peaks want? A 1D array. What is scaled_values? A 2D array. Why.

    df["signal_scaled"] = df.loc[:, "signal"].transform(
        lambda x: (x - x.min()) / (x.max() - x.min())
    )

    peak_idx, peakprops = signal.find_peaks(df.signal_scaled, prominence=0.01)

    plt.plot(df.time, df.signal_scaled, label="scaled_signal")

    plt.plot(
        df.time.iloc[peak_idx],
        df.signal_scaled.iloc[peak_idx],
        "x",
        color="r",
        label="peaks",
    )

    widths, _, _, _ = signal.peak_widths(df.signal_scaled, peak_idx)

    plt.legend()
    plt.show()

    sampling_freq = df.time.diff().mean()

    # widths is measured in index values.

    print(f"The average peak width is {np.mean(widths)} observations")

    print(f"In time units, this is{np.mean(widths*sampling_freq)} mins")

    return None


def calculate_custom_bounds(s: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    Calculate the bounds of the time domain of the peak, (width).
    """
    # lower width is calculated as the time step
    w_lb = s.diff().mean() * 0.5
    # upper bound is calculated as
    w_ub = s.max() - s.min() / 2

    print(w_ub)

    print(f"width lowerbound is: {w_lb}")

    return (w_lb, w_ub)


def get_data(code_idx: int) -> pd.DataFrame:
    db_path = definitions.DB_PATH

    td = testdata.TestData(db_path=db_path)

    rs_kwargs = dict(key="code_wine", x=2)

    # pro_df = td.get_processed_samples(rs_kwargs)

    df = td.get_raw_samples(**rs_kwargs)
    codes = df.code_wine.drop_duplicates()

    df = df.query("code_wine==@codes.iloc[@code_idx]")

    return df


def main():
    oriada111 = get_data(0)

    def sharpen_signal(signal: pd.Series, k: float = 1):
        sharpened_signal = signal - k * signal.diff().diff()

        sharpened_signal.loc[0:1] = signal.loc[0:1]
        return sharpened_signal

    sharpen_weighting = 2

    oriada111["sharp_signal"] = sharpen_signal(oriada111.signal, sharpen_weighting)

    plt.style.use("ggplot")
    fig, ax = plt.subplots(2, 2)

    ax[0][0].plot(oriada111.time, oriada111.signal, label="raw signal", color="red")
    ax[0][1].plot(
        oriada111.time, oriada111["sharp_signal"], label="sharpened", color="blue"
    )

    input_signal = (
        oriada111
        #   .query("time<=2")
    )

    chm = Chromatogram(input_signal)

    chm.correct_baseline(0.7)

    chm.show(ax=ax[1][0])

    chm._assign_windows(prominence=1e-3, rel_height=1)

    num_plots = chm.window_df.window_id.nunique()

    for id, grp in chm.window_df.query("window_type=='peak'").groupby("window_id"):
        # plot each window and its id
        ax[1][1].plot(grp.time, grp.signal_corrected, label="id")
        ax[1][1].annotate(id, xy=[grp.time.median(), grp.signal_corrected.max() * 1.2])

        # plot the detected peaks
        peak_data = chm.df.iloc[chm._peak_indices]
        # ax.scatter(peak_data.time, peak_data.signal_corrected, label='peaks')

        # # annotate each peak
        # for idx, cols in peak_data.reset_index(drop=True).iterrows():

        #     ax.annotate(idx+1, xy=[cols.time, cols.signal_corrected*1.1]

    # deconvolve

    # chm.deconvolve_peaks()

    # chm.show(ax=2)

    plt.show()


if __name__ == "__main__":
    main()
