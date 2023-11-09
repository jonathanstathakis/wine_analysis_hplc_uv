"""
2023-11-08

A module reproducing the pipeline prototyped in: <src/wine_analysis_hplc_uv/notebooks/2023-11-01.pca-xgboost/2023-11-02_prep_reds_dset_for_analysis.ipynb>
"""

from IPython.display import display
import pandas as pd
import numpy as np
from wine_analysis_hplc_uv.notebooks.mcr import mcr_methods
import matplotlib.pyplot as plt


class PCA_Analysis(mcr_methods.Preprocessing, mcr_methods.PCA, mcr_methods.Signal_Anal):
    def __init__(self):
        return None


class DataFrameValidator:
    def validate_dataframe(self, df):
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        return df


class SliceSelection:
    def select_group(
        self, df: pd.DataFrame, var: str, value: str | int | float
    ) -> pd.DataFrame:
        """
        select a subset of the input dataset by specified 'values' in a specified 'variable' column
        """
        return df.loc[lambda df: df[var] == value].reset_index(drop=True)

    def remove_outliers(
        self, df: pd.DataFrame, label_col: str, outlier_label: str | list[str] = []
    ) -> pd.DataFrame:
        """
        Remove identified outlier samples
        """

        assert (
            label_col in df.columns
        ), f"{label_col} is not in df columns. df columns:\n{df.columns}"

        if isinstance(outlier_label, list):
            for label in outlier_label:
                out_df = df.loc[lambda df: ~(df[label_col].str.contains(label))]

        else:
            out_df = df.loc[lambda df: ~(df[label_col].str.contains(outlier_label))]

        # check if the samples have been removed

        for label in outlier_label:
            assert ~df[label_col].str.contains(label).all()

        return out_df


class DataframeAdjuster(DataFrameValidator):
    def adjust_df(
        self,
        df: pd.DataFrame,
        left_colname: str,
        right_colname: str,
        drop_cols: str | list,
    ) -> pd.DataFrame:
        """
        Concatenate label columns to reduce total number of columns, (at this point, supposed to be 'samplecode' + 'wine') and remove unneeded columns
        """

        return (
            df.pipe(self.concat_code_wine, left_colname, right_colname)
            .pipe(self.validate_dataframe)
            .pipe(self.drop_unnecessary_cols, drop_cols)
        )

    def concat_code_wine(self, df: pd.DataFrame, left_colname: str, right_colname: str):
        df.insert(
            loc=0,
            column=f"{left_colname}_{right_colname}",
            value=df[left_colname] + "_" + df[right_colname],
        )

        df = df.drop([left_colname, right_colname], axis=1)

        return df

    def drop_unnecessary_cols(self, df: pd.DataFrame, drop_cols: str | list[str]):
        return df.drop(drop_cols, axis=1)

    def melt_df(
        self,
        df: pd.DataFrame,
        melt_kwgs: dict = dict(),
    ):
        """
        wrapper for pandas melt
        """

        out_df = df.melt(**melt_kwgs).loc[
            :, lambda df: df.columns.drop("mins").insert(-1, "mins").tolist()
        ]

        return out_df

    def pivot_df(self, df: pd.DataFrame, pivot_kwgs: dict = dict()):
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

        out_df = (
            df.pipe(
                lambda df: df
                if display(
                    df.groupby(grouper)
                    .count()
                    .iloc[:, 0]
                    .loc[lambda x: x > 7800]
                    #    .describe()
                )
                else df
            )
            .pipe(
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
            .pipe(
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
        )
        return out_df


class SignalProcessor(PCA_Analysis):
    def smooth_signals(
        self, df: pd.DataFrame, smooth_kwgs: dict() = dict(), append: bool = True
    ):
        """
        Apply SG smoothing on the target col of each signal specified by the grouper.

        append: if True, adds the smoothed column at the end of the df as 'smoothed', else replaces the target_col with the smoothed col.
        """

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


class DataPipeline(SliceSelection, DataframeAdjuster, TimeResampler, SignalProcessor):
    def __init__(
        self,
        in_filepath: str,
        outpath: str,
        select_group_kwgs: dict = dict(),
        adjuster_kwgs: dict = dict(),
        outlier_kwgs: dict = dict(),
        resample_kwgs: dict = dict(),
        melt_kwgs: dict = dict(),
        smooth_kwgs: dict = dict(),
        bline_sub_kwgs: dict = dict(),
        pivot_kwgs: dict = dict(),
    ):
        self.in_filepath_ = in_filepath

        self.raw_data_ = self.load_raw_data(filepath=self.in_filepath_)

        self.processed_df = (
            self.raw_data_.pipe(func=self.validate_dataframe)
            .pipe(func=self.select_group, **select_group_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.adjust_df, **adjuster_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.remove_outliers, **outlier_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.resample_df, **resample_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.melt_df, melt_kwgs=melt_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(func=self.smooth_signals, **smooth_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.subtract_baseline, **bline_sub_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.pivot_df, pivot_kwgs)
            .pipe(func=self.validate_dataframe)
            .pipe(self.output_processed_data, outpath)
        )

    def load_raw_data(self, filepath: str):
        return pd.read_parquet(path=filepath)

    def output_processed_data(self, df: pd.DataFrame, outpath: str):
        df.to_parquet(outpath)
        return None


def main():
    in_filepath = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/tidy_3d_dset_raw.parquet"

    append = True
    dp = DataPipeline(
        in_filepath=in_filepath,
        select_group_kwgs=dict(
            var="color",
            value="red",
        ),
        adjuster_kwgs=dict(
            left_colname="samplecode",
            right_colname="wine",
            drop_cols=["detection", "color"],
        ),
        outlier_kwgs=dict(
            label_col="samplecode_wine",
            outlier_label=["72", "115", "a0301", "99", "98"],
        ),
        resample_kwgs=dict(
            grouper=["id", "samplecode_wine"],
            time_col="mins",
            original_freqstr="0.4S",
            resample_freqstr="2S",
        ),
        melt_kwgs=dict(
            id_vars=["varietal", "id", "samplecode_wine", "mins"],
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
            columns=["varietal", "samplecode_wine", "id", "wavelength"],
            index="mins",
            values="bcorr",
        ),
        outpath="/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/2023-11-05.xgboost/2023-11-09_test.parquet",
    )


if __name__ == "__main__":
    main()
