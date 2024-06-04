"""
2023-08-23 23:30:42

A module destined to replace [this one](./src/wine_analysis_hplc_uv/signal_processing/signal_data_treatment_methods.py). Primarily it differs in that it will have a class API, and expect a multiindexed dataframe as input.
"""

import pandas as pd
import logging
from pybaselines import Baseline
import matplotlib.pyplot as plt
from IPython.display import display
import seaborn as sns
from wine_analysis_hplc_uv.old_signal_processing import sigpro_methods

logger = logging.getLogger(__name__)


class SignalProcessor:
    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        2023-08-23 09:56:10

        Describes a dataframe of the shape:

        samplecode 100       100       200       200
        wine       2000 wine 2000 wine 1998 wine 1998 wine
        vars       mins      value     mins      value
        i
        0           0           5       0           0

        I.e. a 3 level multiindex of ('samplecode','wine','vars') and vars consists of
        ['mins','value'] for each sample. Each samplecode should be unique, wine labels
        are not and are there for human-readability.

        """
        assert df.columns.names[0] == "samplecode", df.columns.names[0]
        assert df.columns.names[1] == "wine"
        assert df.columns.names[2] == "vars"
        assert df.index.name == "i"

        vars_values = df.columns.get_level_values("vars").to_list()
        pattern = ["mins", "value"]
        pat_len = len(pattern)
        assert len(vars_values) % pat_len == 0, "mismatched length of list"
        assert (
            pattern * (len(vars_values) // pat_len) == vars_values
        ), f"incorrect pattern sequence: {vars_values[:4]}"

        # because get_level_values returns 1 label value per sub column, end up with
        # lots of duplicates for higher levels. `DataFrameGroupBy.size()` will be expected
        # to return all groups of the same size. Any groups larger than the average will
        # indicate duplicates.
        df.columns.get_level_values(0).duplicated()

        samplecode = df.columns.get_level_values(0)
        samplecode.value_counts().mode()[0]
        outlier_mask = samplecode.value_counts() > 2
        duplicates = outlier_mask[outlier_mask is True].dropna().index.values

        assert len(duplicates) == 0, duplicates

        logger.info("df validated")
        return df

    def standardize_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        standardize time axis
        """

        df_ = df.pipe(sigpro_methods.standardize_time.standardize_time)

        return df_

    def subtract_baseline(self, df: pd.DataFrame) -> pd.DataFrame:
        """ """

        df = (
            df.pipe(self.long_format)
            .groupby(["samplecode", "wine"], as_index=False)
            .apply(
                lambda grp: grp.assign(
                    baseline=Baseline(grp["mins"].dt.total_seconds()).asls(
                        grp["value"]
                    )[0]
                )
            )
            .droplevel(0)
            .groupby(["samplecode", "wine"], as_index=False)
            .apply(lambda grp: grp.assign(value_bcorr=grp["value"] - grp["baseline"]))
            .droplevel(0)
            # .pipe(lambda df: df.groupby(['samplecode','wine'], as_index=False).apply(plot_baseline_correction))
            .pipe(self.tidy_format)
            .pipe(self.test_subtract_baseline)
        )
        return df

    def test_subtract_baseline(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        2023-08-24 16:34:16
        Test the baseline subtraction by asserting that the area under the baseline
        curve should be less than the area under the original curve. Should cover all
        edge cases..
        """
        from scipy import integrate

        # turn off matplotlib font mangaer debug messages

        mpl_logger = logging.getLogger("matplotlib.font_manager")
        mpl_logger.propagate = False

        def plot_wine(grp: pd.DataFrame) -> pd.DataFrame:
            fig, ax = plt.subplots(1)
            grp.plot(x="mins", y="value", ax=ax, title=grp.index.get_level_values(2)[0])
            grp.plot(x="mins", y="baseline", ax=ax, title="baseline")
            grp.plot(x="mins", y="value_bcorr", ax=ax, title="corr")
            return grp

        def integrate_group(group):
            results = {}
            for col in ["value", "value_bcorr"]:
                results[col] = integrate.trapz(x=group["baseline"], y=group[col])
            return pd.Series(results)

        df = (
            df.pipe(self.long_format)
            .groupby(["samplecode", "wine"])
            .apply(plot_wine)
            .groupby(["samplecode", "wine"])
            .apply(integrate_group)
            .reset_index()
            .pipe(print)
        )

        plt.show()

        return df

    def vars_subplots(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Produces an sns plot of the vars column level

        As usual, requires a columnar multiindexed dataframe with a 0th level 'mins' index
        """
        (
            df.reset_index()
            .melt(id_vars="mins", value_name="v")
            .assign(mins=lambda df: df.mins.dt.total_seconds() / 60)
            .pipe(
                lambda df: sns.FacetGrid(
                    df,
                    col="wine",
                    col_wrap=2,
                    hue="vars",
                    aspect=2,
                    legend_out=True,
                )
                .map(
                    sns.lineplot,
                    "mins",
                    "v",
                    alpha=0.95,
                    # linewidth=1,
                )
                .add_legend()
            )
        )
        return None

    def relplot(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Construct a relplot from a 'value' column for all the samples.
        """
        (
            df.stack(["samplecode", "wine"])
            .reset_index()
            .set_index(["samplecode", "wine", "mins"])
            .drop("i", axis=1)
            .unstack(["samplecode", "wine"])
            .reorder_levels(["samplecode", "wine", "vars"], axis=1)
            .sort_index(level="samplecode", axis=1)
            .droplevel(0, axis=1)
            .reset_index()
            .melt("mins")
            .pipe(sns.relplot, x="mins", y="value", hue="vars", kind="line")
        )
        return df

    def savgol_smooth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply a savitzy-golay smoothing algorithm as per [@cuadros-rodríguez_2021].
        5 point window, 2nd order polynomial.
        """

        from scipy.signal import savgol_filter

        df = (
            df.stack(["samplecode", "wine"])
            .pipe(
                lambda df: df.assign(
                    sval=lambda df: df.groupby(["samplecode"], group_keys=False)[
                        "value"
                    ].apply(
                        lambda group: pd.DataFrame(
                            savgol_filter(group, window_length=5, polyorder=2),
                            index=group.index,
                        )
                    )
                )
            )
            .unstack(["samplecode", "wine"])
        )

        return df

    def zero_y_axis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Assuming that a 1D signal y, y[0] has a non-zero value. Subtract y[0] from y
        to correct the offset.
        """

        out_df = (
            df.stack(["samplecode", "wine"])
            .reorder_levels(["samplecode", "wine", "mins"])
            .sort_index()
            .pipe(
                lambda df: df.groupby(["samplecode"], group_keys=False).apply(
                    lambda df: df.assign(value=lambda df: df.value - df.value[0])
                )
            )
            .unstack(["samplecode", "wine"])
            .reorder_levels(["samplecode", "wine", "vars"], axis=1)
        )

        return out_df

    def baseline_correction(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies asls to correct signal baselines. Returns a midf (multiindexed df)
        with the original signal, the calculated baseline, and the baseline subtracted
        signal.

        as per
        [developing_baseline_subtraction](notebooks/developing_baseline_subtraction.ipynb),
        asls with a lam of 10000 was found to fit the sampleset best.
        """
        from pybaselines import Baseline

        def aslsblinefunc(df: pd.DataFrame) -> pd.DataFrame:
            df = df.assign(
                bline=Baseline(
                    x_data=df.index.get_level_values("mins").total_seconds(),
                    assume_sorted=True,
                ).asls(df["value"], max_iter=50, tol=0.001, lam=10000)[0]
            ).assign(blinesub=lambda df: df.eval("value - bline"))

            return df

        out_df = (
            # move samplecode and wine to index
            df.stack(["samplecode", "wine"])
            # groupby samplecode, excluding the group keys in the output
            .groupby(["samplecode"], group_keys=False)
            # apply the predefined asls baseline fitting algo to each group
            .apply(lambda df: aslsblinefunc(df))
            # rename 'value' to 'signal' to differentiate it from the fitted baseline
            # and baseline subtracted signal column. The idea being that the raw signal
            # is a superset of other signal sets, the noise set, the true signal set,
            # etc.
            .rename(mapper={"value": "signal"}, axis=1)
            # melt the frame while preserving the index to merge the 'signal', 'bline'
            # and 'blinesub' column values to one column with a label column in order
            # to reassign the labels as an ordered categorical index with name
            # 'subsignal'
            .melt(ignore_index=False, var_name="subsignal")
            # reassign the signal label column to the frame as an ordered categorical
            # index
            .assign(
                subsignal=lambda df: pd.Categorical(
                    df.subsignal,
                    categories=["signal", "bline", "blinesub"],
                    ordered=True,
                )
            )
            # reset the three level multiindex index to prepare for pivoting to tidy
            # form
            .reset_index()
            # pivot from long to tidy with column heirarchy 'samplecode','wine',
            # 'subsignal', index of 'mins'
            .pivot(
                columns=["samplecode", "wine", "subsignal"],
                index="mins",
                values="value",
            )
            # sort the column multiindex for visual clarity
            .sort_index(axis="columns")
        )

        return out_df

    def unique_wine_label(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Form label dataframe from multiindex, form label column as concat of wine + cumcount+1.
        Join with label column on samplecode index, use label column to map to wine, fill it
        where NA with wine value (i.e. unique wine names) then replace wine column with label
        through assign.
        """
        # add the label as a concatentation of cumcount+1 and wine name

        labels = (
            df.columns.to_frame()
            .reset_index(drop=True)[["samplecode", "wine"]]
            .set_index("samplecode")[lambda df: df.duplicated(keep=False)]
            .assign(
                label=lambda df: df["wine"]
                + " "
                + df.groupby(["wine"]).cumcount().add(1).astype(str)
            )
        )

        # go to long format, join with label df on samplecode, merge label and wine column via
        # where, replace wine column with the merge, go back to tidy format

        df = (
            df.stack(["samplecode", "wine"])
            .reset_index("mins")
            .join(labels["label"])
            .rename_axis("vars", axis=1)
            .reset_index()
            .pipe(
                lambda df: df.assign(
                    wine=df["label"].where(~df["label"].isna(), df["wine"])
                )
            )
            .drop(["label"], axis=1)
            .set_index(["samplecode", "wine", "mins"])
            .unstack(["samplecode", "wine"])
            .reorder_levels(axis=1, order=["samplecode", "wine", "vars"])
            .sort_index(axis=1, level="samplecode")
        )

        return df

    def most_correlated(self, df: pd.DataFrame, signal_label: str) -> str:
        """
        Takes a tidy df of columns ['samplecode','wine','subsignal'], identifies the reference and
        Returns a tidy df of columns ['role','samplecode','wine','subsignal'] with index 'mins', column sorted, where the reference is labelled in the 'role' column level.



        See [identifying_most_similar_signal](notebooks/identifying_most_similar_signal.ipynb) for more information.

        As of 2023-10-16 this method Assumes a column level order of ['samplecode','wine','subsignal']

        NOTE: as of 2023-10-16 the subsignal assignment as Categorical section of the chain should not be necessary but for some reason the column is cast to object when melting from multiindexed columns.
        """

        # Identify the reference samplecode as that which corresponds to the sample with the most correlated signal determined as the signal with the highest mean correlation value in the correlation matrix. Note that this is based on the blinesub subsignal, different results may occur if the raw 'signal' is used.

        ref_samplecode = (
            df.loc[:, pd.IndexSlice[:, :, signal_label]]
            .corr()
            .mean()
            .sort_values(ascending=False)
            .loc[lambda df: df == df.max()]
            .index.get_level_values("samplecode")
        )

        # add a column level 'role' that distinguishes the determined 'ref' from the 'query' samples. NOTE that this is based on the
        a = (
            df
            # melt to long format while retaining 'mins' index
            .melt(ignore_index=False)
            # assign a 'role' ordered categorical column initally all 'query'
            .assign(
                role=lambda df: pd.Categorical(
                    values=["query"] * len(df.index),
                    categories=["ref", "query"],
                    ordered=True,
                )
            )
            # where samplecode matches 'ref_samplecode', replace 'query' with 'ref'
            .assign(
                role=lambda df: df["role"].where(
                    ~(df.samplecode == ref_samplecode.values[0]), "ref"
                )
            )
            # TEMPORARY FIX: reassign subsignal as an ordered categorical column
            .assign(
                subsignal=lambda df: pd.Categorical(
                    df.subsignal,
                    categories=["signal", "bline", signal_label],
                    ordered=True,
                )
            )
            # reset index to prepare for pivot
            .reset_index()
            # pivot to tidy format with role as top level
            .pivot(
                index="mins",
                columns=["role", "samplecode", "wine", "subsignal"],
                values="value",
            )
            .sort_index(axis=1)
        )

        return a

    def dynamic_time_warping(self, df: pd.DataFrame, signal_label: str) -> pd.DataFrame:
        """
        Contain the method to align a given dataset on a reference using the baseline
        subtracted signals.

        As per a design paradigm defined on 2023-10-16: within reason, no mutations
        should occur to columns within a dataframe, only additions to the dataframe,
        this method adds an aligned column to the subsignal level alongside the other
        intermediate signals such as 'signal', and 'blinesub'.
        """

        from dtwalign import dtw

        idx = pd.IndexSlice
        # subset the frame by 'subsignal' to get the bline_sub of each sample

        def align_query_to_ref(query, ref, ax=None):
            # calculate the warping path to align x to y
            dtw_obj = dtw(
                x=query.value, y=ref, window_type="sakoechiba", window_size=10
            )

            # subset signal by warping path
            aligned_query = query.iloc[dtw_obj.get_warping_path()]

            # reassign index as timedelta_range with freq '2S' to smooth out
            # irregularities generated by subsetting by the warping path
            new_timedelta = pd.timedelta_range(
                start=aligned_query.index[0], end=aligned_query.index[-1], freq="2S"
            )

            aligned_query = aligned_query.set_axis(
                pd.TimedeltaIndex(
                    new_timedelta, freq="2S", name=aligned_query.index.name
                )
            )

            # relabel 'subsignal' as 'aligned'
            aligned_query = aligned_query.assign(subsignal="aligned")

            return aligned_query

        # find the samplecode value for the most correlated sample
        df = df.pipe(self.most_correlated, signal_label)

        # calculate the alignment

        ref_signal = df.loc[:, idx["ref", :, :, signal_label]]

        aligned_df = (
            df.loc[:, idx[:, :, :, signal_label]]
            .melt(ignore_index=False)
            .groupby(["samplecode"], group_keys=False)
            .apply(align_query_to_ref, ref_signal)
        )

        long_df = df.melt(ignore_index=False)

        long_df_multiindex = long_df.set_index(
            ["role", "samplecode", "wine", "subsignal"], append=True
        )

        long_aligned_df_multiindex = aligned_df.set_index(
            ["role", "samplecode", "wine", "subsignal"], append=True
        )

        out_df = pd.concat([long_aligned_df_multiindex, long_df_multiindex])

        tidy_out_df = (
            out_df.reset_index()
            .pivot(
                columns=["role", "samplecode", "wine", "subsignal"],
                index="mins",
                values="value",
            )
            .sort_index(axis=1)
        )

        return tidy_out_df

    def propipe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        The full pipe to lead to a processed dataset
        """

        pro_df = (
            df
            # df.pipe(self.unique_wine_label)
            .pipe(self.standardize_time)
            .pipe(self.downsample_signal, "2S")
            .pipe(self.zero_y_axis)
            .pipe(self.baseline_correction)
            .pipe(lambda df: df if display(df) else df)  # display df
        )

        return pro_df
