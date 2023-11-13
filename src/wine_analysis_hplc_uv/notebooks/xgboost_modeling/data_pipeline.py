"""
2023-11-08

A module reproducing the pipeline prototyped in: <src/wine_analysis_hplc_uv/notebooks/2023-11-01.pca-xgboost/2023-11-02_prep_reds_dset_for_analysis.ipynb>
"""

from IPython.display import display
import pandas as pd
import numpy as np
from wine_analysis_hplc_uv.notebooks.mcr import mcr_methods
import matplotlib.pyplot as plt
from wine_analysis_hplc_uv.signal_processing import signal_processing
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract
from wine_analysis_hplc_uv import definitions
import logging

logger = logging.getLogger(__name__)


class DataFrameValidator:
    def validate_dataframe(self, df):
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        return df


class DataframeAdjuster(DataFrameValidator):
    def melt_df(
        self,
        df: pd.DataFrame,
        melt_kwgs: dict = dict(),
    ):
        """
        wrapper for pandas melt
        """

        logger.info(f"Melting df with {melt_kwgs}..")

        out_df = df.melt(**melt_kwgs).loc[
            :, lambda df: df.columns.drop("mins").insert(-1, "mins").tolist()
        ]

        return out_df

    def pivot_df(self, df: pd.DataFrame, pivot_kwgs: dict = dict()):
        logging.info(f"pivoting df with {pivot_kwgs}..")
        out_df = df.pivot_table(**pivot_kwgs).sort_index(axis=1)

        return out_df


class TimeResampler:
    def resample_df(
        self,
        df: pd.DataFrame,
        grouper: str | list[str],
        time_col: str,
        original_freqstr: str,
        resample_freqstr: str,
    ) -> pd.DataFrame:
        """
        Treat the dataframe as a time series and resample to the specified sampling rate.

        df: the intended dataframe, in wide format with observations as rows containing 'time_col'

        grouper: label columns to seperate each sample wavelength signal. each group needs to have 'time_col' start at the first observation and end at the last observation for the results to make sense.

        original_freqstr: the frequency string corresponding to the original frequency of observations. Due to instrument error, the sampling frequency can vary minutely, and occasionally an observation can be missed. Resampling the time column to a specified frequency smooths out irregularities and enables proper resampling.

        resample_freqstr: frequency string corresponding to the destination sampling frequency.
        """

        logger.info(
            f"resampling to {original_freqstr} to remove irregularities between samples.."
        )

        time_normalized_df = df.pipe(
            lambda df: df.assign(
                **{
                    time_col: lambda x: x.groupby(grouper)[time_col].transform(
                        lambda x: pd.timedelta_range(
                            start=0, periods=len(x), freq=original_freqstr
                        ).total_seconds()
                        / 60
                    )
                }
            )
        )

        logger.info(f"Resampling to {resample_freqstr}..")

        resampled_df = time_normalized_df.pipe(
            lambda df: df.assign(
                **{time_col: pd.TimedeltaIndex(data=df.loc[:, time_col], unit="m")}
            )
            .set_index(time_col)
            .groupby(grouper, as_index=False, group_keys=False)
            .apply(lambda grp: grp.resample(resample_freqstr).interpolate().ffill())
            .set_index(grouper, append=True)
            .reset_index("mins")
            .reset_index()
            .assign(
                **{time_col: lambda df: df.loc[:, time_col].dt.total_seconds() / 60}
            )
        )

        return resampled_df


class SignalProcessor(signal_processing.Preprocessing):
    def smooth_signals(
        self, df: pd.DataFrame, smooth_kwgs: dict() = dict(), append: bool = True
    ):
        """
        Apply SG smoothing on the target col of each signal specified by the grouper.

        append: if True, adds the smoothed column at the end of the df as 'smoothed', else replaces the target_col with the smoothed col.
        """

        logger.info(f"Smoothing signal with {smooth_kwgs}..")

        if append:
            out_df = df.assign(smoothed=lambda df: df.pipe(self._smooth, **smooth_kwgs))

        else:
            out_df = df.assign(
                **{smooth_kwgs["col"]: df.pipe(self._smooth, **smooth_kwgs)}
            )

        return out_df

    def subtract_baseline(
        self,
        df: pd.DataFrame,
        prepro_bline_sub_kwgs: dict = dict(asls_kws=dict()),
        append: bool = True,
    ):
        """
        Apply baseline correction using asls.

        append: if True, adds the subtracted column at the end of the df as 'bcorr',
        else replaces the target col with the baseline subtracted col.
        """

        if append:
            out_df = df.assign(
                bcorr=lambda df: df.pipe(
                    self._baseline_subtract, **prepro_bline_sub_kwgs
                )
            )

        else:
            out_df = df.assign(
                **{
                    prepro_bline_sub_kwgs["col"]: df.pipe(
                        self._baseline_subtract, **prepro_bline_sub_kwgs
                    )
                }
            )

        return out_df


class DataPipeline(
    dataextract.DataExtractor,
    DataframeAdjuster,
    TimeResampler,
    SignalProcessor,
):
    def __init__(
        self,
        db_path: str,
    ):
        dataextract.DataExtractor.__init__(self, db_path=db_path)

    def process_frame(
        self,
        resample_kwgs: dict = dict(),
        melt_kwgs: dict = dict(),
        smooth_kwgs: dict = dict(),
        bline_sub_kwgs: dict = dict(),
        pivot_kwgs: dict = dict(),
    ) -> pd.DataFrame:
        self.processed_df = (
            self.raw_data_.pipe(func=self.resample_df, **resample_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.melt_df, melt_kwgs=melt_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.smooth_signals, **smooth_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.subtract_baseline, **bline_sub_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.pivot_df, pivot_kwgs)
            .pipe(func=self.validate_dataframe)
        )

    def output_processed_data(self, outpath: str):
        logging.info(f"output to {outpath}")

        self.processed_df.to_parquet(outpath)

        return None
