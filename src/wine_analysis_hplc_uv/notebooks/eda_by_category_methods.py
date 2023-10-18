"""
2023-10-17

Secondary methods defined during the development of [Chapter: Signal EDA by Category](./chapter.results.signal_eda_by_category.ipynb)
"""
import numpy as np
import seaborn as sns
import seaborn.objects as so
import pandas as pd
from scipy import signal
from dtwalign import dtw
import pandas as pd
from wine_analysis_hplc_uv import definitions
import seaborn as sns
import seaborn.objects as so
from wine_analysis_hplc_uv.notebooks.dtw_methods import DTWNotebookMethods
from wine_analysis_hplc_uv.signal_processing.mindex_signal_processing import (
    SignalProcessor,
)
import seaborn as sns

sns.set_theme(rc={"figure.dpi": 200})
import matplotlib.pyplot as plt
from wine_analysis_hplc_uv.notebooks import eda_by_category_methods
import matplotlib as mpl
import matplotlib.pyplot as plt
from pybaselines import Baseline
import numpy as np

from IPython.display import display

scipro = SignalProcessor()


class Plotting:
    def alignment_heatmap(self, data, ax, signal_label):
        """
        Produce a heatmap of the dataset to signify level of alignment between peaks.

        Currently (2023-10-17) expects a datetime index and 4 level column multiindex with
        signal as the 4th level. Subsets 16 minutes which was the area of interest for the
        test dataset
        """

        hm_data = (
            data
            # convert index to float
            .pipe(
                lambda df: df.set_axis(
                    axis=0, labels=np.round((df.index.total_seconds() / 60), 2)
                )
            )
            # slice to baseline corrected signal and 16 mins
            .loc[:16, pd.IndexSlice[:, :, :, signal_label]]
            # remove 'signal' level
            .pipe(
                lambda df: df.set_axis(axis=1, labels=df.columns.droplevel("subsignal"))
                # flatten multiindex column labels and restrict to thirty char
            ).pipe(
                lambda df: df.set_axis(
                    axis=1,
                    labels=[
                        ".".join(label).replace(" ", "-")[:30]
                        for label in df.columns.to_flat_index()
                    ],
                )
            )
        )

        # instantiate the heatmap Axes object
        hm = sns.heatmap(hm_data, ax=ax)

        # set y tick labels to 5 values evenly spaced

        labels = hm_data.index[:: int(len(hm_data.index) / 5)]
        yticks = hm.set_yticks(
            ticks=np.linspace(start=0, stop=len(hm_data.index), num=len(labels)),
            labels=labels,
        )

        # rotate the xtick labels to 20 degrees to save space
        [tick.set_rotation(20) for tick in hm.get_xticklabels()]
        return hm
