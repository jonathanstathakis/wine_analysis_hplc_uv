"""
2023-11-16 08:56:48

2023-11-17 08:57:57

TODO:
- [ ] get peak indexes out of `fit_peaks` to enable joining of the peak table to the source signal
- [ ] construct a peak overlay plot, preferably with demonstration of how the peak area has been calculated
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
import numpy as np
import seaborn.objects as so
import pandas as pd
from hplc_py.quant import Chromatogram
from wine_analysis_hplc_uv.notebooks.peak_deconv import testdata

import logging

logger = logging.basicConfig(level="DEBUG")


class HPLCPy:
    def __init__(self, data):
        in_data = data[["mins", "signal"]].rename({"mins": "time"}, axis=1)

        chm = Chromatogram(in_data)

        peaks = chm.fit_peaks(
            correct_baseline=False,
            prominence=0.5,
        )

        in_data.time = pd.TimedeltaIndex(
            in_data.time.transform(np.round, decimals=4), unit="m"
        )
        peaks.retention_time = pd.TimedeltaIndex(peaks.retention_time, unit="m")

        print(peaks)

        import sys

        sys.exit()

        orig_signals = in_data.signal.iloc[33, 51, 84].values

        print(orig_signals)
        peaks["signal"] = orig_signals

        print(peaks)

        (
            so.Plot(in_data, x="time", y="signal")
            .add(so.Line())
            .add(so.Dot(), data=peaks, x="retention_time", y="signal")
            .show()
        )

        chm.show()


def main():
    db_path = definitions.DB_PATH
    # data = datasets.RawRedVarietalData(db_path).pro_data_
    data = (
        testdata.TestData(db_path=db_path)
        .pro_data_.melt(value_name="signal", ignore_index=False)
        .reset_index()
    )

    singlesample = data.groupby("code_wine").get_group(data.code_wine.iloc[0])

    # test_data.signal=test_data.signal.transform(lambda x: x-x.min())

    # the guess is not within the bounds.
    print("starting")
    # HPLCPy(data)
    HPLCPy(singlesample)


if __name__ == "__main__":
    main()
