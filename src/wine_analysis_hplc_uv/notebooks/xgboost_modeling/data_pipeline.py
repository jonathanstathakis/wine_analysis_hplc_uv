"""
2023-11-08

A module reproducing the pipeline prototyped in: <src/wine_analysis_hplc_uv/notebooks/2023-11-01.pca-xgboost/2023-11-02_prep_reds_dset_for_analysis.ipynb>

todo: rewrite doc strings for all methods
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


class DataframeValidationMixin:
    """
    Contains methods for validating dataframes
    """

    def validate_dataframe(self, df):
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        return df


class DataframeAdjusterMixin:
    """
    Methods for adjusting a dataframe, currently just wrappers for melt and pivot
    """

    def melt_df(
        self,
        df: pd.DataFrame,
        melt_kwgs: dict = dict(),
    ) -> pd.DataFrame:
        """
        wrapper for pandas melt. Input melt kwargs as a dict, returns the melted df
        """

        logger.info(f"Melting df with {melt_kwgs}..")

        out_df = df.melt(**melt_kwgs).loc[
            :, lambda df: df.columns.drop("mins").insert(-1, "mins").tolist()
        ]

        return out_df

    def pivot_df(
        self, df: pd.DataFrame, pivot_tbl_kwgs: dict = dict(), bypass: bool = False
    ) -> pd.DataFrame:
        """
        pivot_df wrapper for pivot.

        Input the kwargs for pivot as a dict and outputs the pivoted df

        :param df: a dataframe, generally a long one
        :type df: pd.DataFrame
        :param pivot_kwgs: refer to [docs](https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html), defaults to dict()
        :type pivot_kwgs: dict, optional
        :return: pivoted df
        :rtype: pd.DataFrame
        """
        if not bypass:
            logging.info(f"pivoting df with {pivot_tbl_kwgs}..")
            out_df = df.pivot_table(pivot_tbl_kwgs).sort_index(axis=1)

        else:
            out_df = df

        return out_df


"""
Treat the dataframe as a time series and resample to the specified sampling rate.

df: the intended dataframe, in wide format with observations as rows containing 'time_col'

grouper: label columns to seperate each sample wavelength signal. each group needs to have 'time_col' start at the first observation and end at the last observation for the results to make sense.

original_freqstr: the frequency string corresponding to the original frequency of observations. Due to instrument error, the sampling frequency can vary minutely, and occasionally an observation can be missed. Resampling the time column to a specified frequency smooths out irregularities and enables proper resampling.

resample_freqstr: frequency string corresponding to the destination sampling frequency.
"""


class TimeResamplerMixin:
    def resample_df(
        self,
        df: pd.DataFrame,
        grouper: str | list[str],
        time_col: str,
        original_freqstr: str,
        resample_freqstr: str,
    ) -> pd.DataFrame:
        """
        resample_df resample dataframe to specified sampling rate

        Treating the columns of a dataframe as time series on the same time axis, resample them up or down to the frequency specified in 'resample_freqstr`. Returns the resampled dataframe

        Note: this function takes care of converting non-timedelta columns to timedelta, but should work with a timedelta input. Refer to [docs](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects) regarding valid strings.

        :param df: a dataframe containing columnar time series all on the same time axis, with a timedelta column
        :type df: pd.DataFrame
        :param grouper: For long frames with stacked samples, group by `grouper` then apply resampling groupwise
        :type grouper: str | list[str]
        :param time_col: the column to be used as the timedelta index, i.e. 'mins'
        :type time_col: str
        :param original_freqstr: The original frequency of the time series axis as defined as 1/T where T is Hz.
        :type original_freqstr: str
        :param resample_freqstr: The destination frequency
        :type resample_freqstr: str
        :return: a resampled dataframe
        :rtype: pd.DataFrame
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


class SignalProcessorMixin(signal_processing.Preprocessing):
    def smooth_signals(
        self, df: pd.DataFrame, smooth_kwgs: dict() = dict(), append: bool = True
    ) -> pd.DataFrame:
        """
        smooth_signals apply SG smoothing to a target column

        Applies Savitzky-Golay smoothing to 'col', either replacing the column or appending it to the end of the dataframe. Refer to [docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html) for kwargs.

        :param df: dataframe containing a column to be smoothed
        :type df: pd.DataFrame
        :param smooth_kwgs: kwargs passed to the SG function, defaults to dict()
        :type smooth_kwgs: dict, optional
        :param append: If `True`, smoothed column is added to the end of the input dataframe, else it replaces the input column, defaults to True
        :type append: bool, optional
        :return: DataFrame containinng the smoothed column
        :rtype: pd.DataFrame
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
        df: pd.DataFrame = pd.DataFrame(),
        prepro_bline_sub_kwgs: dict = dict(asls_kws=dict()),
        append: bool = True,
        bypass: bool = False,
    ) -> pd.DataFrame:
        """
        subtract_baseline Apply baseline correction via asls

        Uses ASLS to calculate a baseline for a given input column then subtracts the baseline from the signal. Either returns a DataFrame with the baseline corrected signal appended to the end or replacing the signal.

        :param df: A DataFrame containing a signal needing baseline correction
        :type df: pd.DataFrame
        :param prepro_bline_sub_kwgs: kwargs to pass to `preprocessing._baseline_subtract`, defaults to dict(asls_kws=dict())
        :type prepro_bline_sub_kwgs: dict, optional
        :param append: if `True`, appends the baseline corrected signal to the end of the DataFrame, else replaces the input column, defaults to True
        :type append: bool, optional
        :return: a DataFrame containing the baseline corrected signal
        :rtype: pd.DataFrame
        """

        if not bypass:
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
        else:
            out_df = df
        return out_df


class DataPipeline(
    DataframeAdjusterMixin,
    TimeResamplerMixin,
    SignalProcessorMixin,
    DataframeValidationMixin,
):
    def __init__(
        self,
        resample_kwgs: dict = dict(),
        melt_kwgs: dict = dict(),
        smooth_kwgs: dict = dict(),
        bline_sub_kwgs: dict = dict(),
        pivot_kwgs: dict = dict(),
    ):
        self.resample_kwgs = resample_kwgs
        self.melt_kwgs = melt_kwgs
        self.smooth_kwgs = smooth_kwgs
        self.bline_sub_kwgs = bline_sub_kwgs
        self.pivot_kwgs = pivot_kwgs

        # self.processed_data_ = self.signal_preprocess()

    def signal_preprocess(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        TODO:
        update docstring

        process_frame Pipeline function performing necessary signal processing transformations to remove noise and reduce the dataset size prior to modeling.

        Before EDA and modeling it is necessary to compress the dataset through resampling, smooth, and baseline subtract. This function wraps a Pandas pipe actioning these steps on an input DataFrame which starts in long form with samples observations as rows, i.e. [sample1],[sample2],..,[sample_n] where row 1 of sample 1 is observation 0, and row n of sample 1 is observation n, and label columns, a time column 'mins' and signal columns ('nm_256', for example).

        This function takes the input DataFrame, and dicts of kwargs for each step of the pipeline, and returns a tidy format dataframe with samples as columns with observations as rows.

        :param _raw_data: A long augmented DataFrame of stacked samples with label columns, a time column 'mins' and at least one signal column with a label like "nm_*"
        :type _raw_data: pd.DataFrame
        :param resample_kwgs: see `TimeResamplerMixin.resample_df` , defaults to dict()
        :type resample_kwgs: dict, optional
        :param melt_kwgs: melt kwargs, defaults to dict()
        :type melt_kwgs: dict, optional
        :param smooth_kwgs: see `SignalProcessorMixin.smooth_signals`, defaults to dict()
        :type smooth_kwgs: dict, optional
        :param bline_sub_kwgs: see `SignalProcessorMixin.subtract_baseline`, defaults to dict()
        :type bline_sub_kwgs: dict, optional
        :param pivot_kwgs: see `DataFrameAdjusterMixin.pivot_df`, defaults to dict()
        :type pivot_kwgs: dict, optional
        :return: A tidy format processed dataframe with samples as columns and observations as rows
        :rtype: pd.DataFrame
        """
        self._pro_data = (
            raw_data.pipe(func=self.resample_df, **self.resample_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.melt_df, melt_kwgs=self.melt_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.smooth_signals, **self.smooth_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.subtract_baseline, **self.bline_sub_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.pivot_df, **self.pivot_kwgs)
            .pipe(func=self.validate_dataframe)
        )

        return self._pro_data


def main():
    append = True
    dp = DataPipeline(
        db_path=definitions.DB_PATH,
    )

    dp.create_subset_table(
        detection=("raw",),
        exclude_samplecodes=(["72", "115", "a0301", "99", "98"]),
        wavelengths=(256),
    )

    dp.signal_preprocess(
        resample_kwgs=dict(
            grouper=["id", "code_wine"],
            time_col="mins",
            original_freqstr="0.4S",
            resample_freqstr="2S",
        ),
        melt_kwgs=dict(
            id_vars=["detection", "color", "varietal", "id", "code_wine", "mins"],
            value_name="signal",
            var_name="wavelength",
        ),
        smooth_kwgs=dict(
            smooth_kwgs=dict(
                grouper=["id", "wavelength"],
                col="signal",
            ),
            append=append,
        ),
        bline_sub_kwgs=dict(
            prepro_bline_sub_kwgs=dict(
                grouper=["id", "wavelength"],
                col="smoothed",
                asls_kws=dict(max_iter=100, tol=1e-3, lam=1e5),
            ),
            append=append,
        ),
        pivot_kwgs=dict(
            columns=["detection", "color", "varietal", "id", "code_wine"],
            index="mins",
            values="bcorr",
        ),
    )

    dp.output_processed_data(
        outpath="/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/xgboost_modeling/2023-11-12.parquet",
    )


if __name__ == "__main__":
    main()
