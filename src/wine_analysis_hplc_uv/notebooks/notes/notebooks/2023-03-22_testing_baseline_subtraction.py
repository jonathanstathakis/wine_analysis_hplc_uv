import pandas as pd

from scipy.stats import norm

import numpy as np

import matplotlib.pyplot as plt

from numpy.random import default_rng

"""
I need:

1. 2 signals stored in a dataframe within a Dataframe column
2. 2 corresponding baselines stored in a Dataframe Column within the top level df
3. 
"""
rng = default_rng()

signal_1 = rng.standard_normal(501)

# to be similar in format to my actual data, the mins of the signal will run from 0 to 51 mins, divided into the same number of points as the signal.
mins = np.arange(0, 51, 51 / len(signal_1))

# the first signal as a dataframe.
signal_1_df = pd.DataFrame(
    signal_1, columns=["signal"], index=pd.Index(mins, name="mins")
)
signal_1_df.name = "signal_1"

# second signal
signal_2 = rng.standard_normal(501)
signal_2_df = pd.DataFrame(
    signal_2, columns=["signal"], index=pd.Index(mins, name="mins")
)
signal_2_df.name = "signal_2"

# join the signals together into a Series
run_signal_series = pd.Series([signal_1_df, signal_2_df], index=["run_1", "run_2"])
run_signal_series.name = "signals"

# turn it into a df
top_df = run_signal_series.to_frame()

# add metadata column
top_df["acq_times"] = ["14:30", "16:00"]

pd.options.display.max_columns = None

pd.options.display.min_rows = 10

pd.options.display.max_colwidth = 100

# Calculate baselines

from pybaselines import Baseline

baseline_fitter = Baseline(top_df.loc["run_1", "signals"].index)

baselines = (
    top_df["signals"]
    .apply(
        lambda signal: pd.DataFrame(
            baseline_fitter.iasls(signal["signal"])[0],
            index=top_df.loc["run_1", "signals"].index,
            columns=["baseline"],
        )
    )
    .to_frame(name="baselines")
)

corrected_signals = []


def signal_corrector(index: pd.Index, signal: pd.DataFrame):
    if signal.index.equals(baselines["baselines"][index].index):
        try:
            signal = signal["signal"]

            baseline = baselines["baselines"][index]["baseline"]

            corrected_signal = signal - baseline
            corrected_signal.name = "signal"

            corrected_signal = corrected_signal.to_frame()
            corrected_signal.name = f"corrected_{signal.name}"

            return corrected_signal

        except Exception as e:
            print(e)


corrected_signals = []

for index in top_df["signals"].index:
    corrected_signals.append(signal_corrector(index, top_df["signals"][index]))
"""
Time to subtract the baselines from the peaks. The signals are accessed through `top_df['signals]'
"""

# corrected signals are a list of dataframes, each dataframe representing each signal of each run. For this exercise there is only 1 signal per run, but we're practicing this technique to expand to n number of signals per run.

# We want this list to be part of the top_df dataframe. Let's try simply adding as a new column.

top_df["corrected_signals_with_loop"] = corrected_signals

# that works. lets try doing the same with apply statements and then compare the two with equals()
# for each row of top_df['signals] take the index
try:
    corrected_signals_2 = top_df.drop("corrected_signals_with_loop", axis=1).apply(
        func=lambda row: signal_corrector(row.name, row["signals"]),
        axis=1,
    )

    corrected_signals_2.name = "corrected_signals"
except Exception as e:
    print(e)

top_df["corrected_signals"] = corrected_signals_2
