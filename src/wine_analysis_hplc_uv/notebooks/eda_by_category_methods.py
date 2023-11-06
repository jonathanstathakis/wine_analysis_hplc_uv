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


class DTWProcessing:
    def std_time(self, data):
        odata = (
            data.dropna()
            .pipe(scipro.standardize_time)
            .pipe(lambda df: df.set_axis(axis=0, labels=df.index.total_seconds() / 60))
            .droplevel("vars", axis=1)
        )

        return odata

    def smooth(
        self, data: pd.DataFrame, grouper: str, signal_label: str, smoothed_label: str
    ):
        odata = (
            data.melt(ignore_index=False, value_name=signal_label).reset_index()
            # smooth signal with window length 5 and polynomial order 2
            .assign(
                **{
                    smoothed_label: lambda df: df.groupby(grouper)[
                        signal_label
                    ].transform(
                        func=signal.savgol_filter, **dict(window_length=5, polyorder=2)
                    )
                }
            )
        )
        return odata

    def blinecorr(
        self, data: pd.DataFrame, grouper: str, signal: str, bcorr_label: str
    ):
        odata = data.assign(
            bline=lambda df: df.groupby(grouper)[signal].transform(
                lambda x: Baseline(x.index).asls(x)[0]
            )
        ).eval(f"{bcorr_label}={signal}-bline")

        return odata


class Peaks:
    def peakdetect(
        self,
        data: pd.DataFrame,
        grouper: str | list,
        signal_label: str,
        col_label: str,
        findpeaks_kwargs: dict() = dict(),
    ):
        odata = data.assign(
            **{
                col_label: lambda df: df.groupby(grouper)[signal_label].transform(
                    lambda x: x.iloc[signal.find_peaks(x, **findpeaks_kwargs)[0]]
                )
            }
        )

        return odata

    def top_peaks(
        self,
        data: pd.DataFrame,
        grouper: str | list,
        peak_label: str,
        n: int,
        col_label: str,
    ):
        odata = data.assign(
            **{
                col_label: lambda df: df.groupby(grouper, group_keys=False)[
                    peak_label
                ].nlargest(n)
            }
        )

        return odata

    def peak_table(
        self,
        data,
        grouper: str | list,
        peaks_label: str,
        peak_num_label: str,
        peak_idx_label: str,
    ):
        """
        data: long form dataframe with a detected peaks column

        grouper: primary key index column label, or labels for multiple column keys

        peaks_label: the label for the column containing the detected peaks

        peak_num_label: desired label for the column containing the peak count, also
        the index of the outputted table

        peak_idx_label: the label for the index column of the peaks in the source data,
        generally the time column

        Return: tidy table of sample x peaks indexed by peak number

        TODO: add internal validation
        """

        odata = data.pipe(
            lambda df: df.loc[:, ["samplecode", "wine", "mins", peaks_label]]
            .dropna()
            .assign(**{peak_num_label: lambda df: df.groupby(grouper).cumcount()})
            .pivot_table(
                columns=grouper,
                index=peak_num_label,
                values=[peak_idx_label, peaks_label],
            )
            .reorder_levels([1, 2, 0], axis=1)
            .sort_index(axis=1)
        )

        return odata


class ApplyDTW:
    def align(
        self, data, primary_key, siglabel, aligned_label: str, kwargs: dict = dict()
    ):
        """
        For a passed long format df find the reference signal and align, assigning back
        to the passed frame

        TODO: add internal validation
        """

        ref_idx = self.find_ref(data, primary_key, siglabel)

        ref_signal = data.loc[lambda df: df.samplecode == ref_idx][siglabel]

        adata = data.assign(
            **{
                aligned_label: data.groupby(primary_key)[siglabel].transform(
                    self.applydtw, ref_signal, **kwargs
                )
            }
        )

        return adata

    def applydtw(self, query, ref, kwargs: dict = dict()):
        """
        apply dtw
        """
        # subset signal by warping path
        # reset index to enable reindexing after Apply functions (i.e. transform),
        # otherwise get duplicate index error

        aligned_query = (
            query.iloc[dtw(x=query, y=ref, **kwargs).get_warping_path()]
            .reset_index(drop=True)
            .values
        )

        aligned_s = pd.Series(aligned_query, index=query.index)

        return aligned_query

    def find_ref(self, data, primary_key: str, siglabel: str) -> str:
        """
        pass long form df and return the idx string for the reference sample
        """

        tidy_data = data.pivot_table(index="mins", columns=primary_key, values=siglabel)

        ref_idx = tidy_data.corr().mean().loc[lambda df: df == df.max()].index[0]
        return ref_idx
