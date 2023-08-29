"""
2023-08-23 23:30:42

A module destined to replace [this one](./src/wine_analysis_hplc_uv/signal_processing/signal_data_treatment_methods.py). Primarily it differs in that it will have a class API, and expect a multiindexed dataframe as input.
"""

import pandas as pd
import logging
from pybaselines import Baseline
import matplotlib.pyplot as plt

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
        mask = df.columns.get_level_values(0).duplicated()

        samplecode = df.columns.get_level_values(0)
        mode = samplecode.value_counts().mode()[0]
        outlier_mask = samplecode.value_counts() > 2
        duplicates = outlier_mask[outlier_mask == True].dropna().index.values

        assert len(duplicates) == 0, duplicates

        logger.info("df validated")
        return df

    def adjust_timescale(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Refer to
        [Determining Time Precision](notebooks/determining_time_precision.ipynb). It
        has been determined that the minimum level of precision that ensures that each
        time axis value is unique. This is achieved by first converting each mins
        value to timedelta then rounding to millisecond "L".

        """
        df = (
            df.pipe(self.validate_dataframe)
            .stack(["samplecode", "wine"])
            .pipe(
                lambda df: df.assign(
                    mins=pd.to_timedelta(df.loc[:, "mins"], unit="minutes").round("L")
                )
            )
            .unstack(["samplecode", "wine"])
            .reorder_levels(["samplecode", "wine", "vars"], axis=1)
            .sort_index(axis=1, level=1, sort_remaining=True)
            .pipe(self.validate_dataframe)
            .pipe(self.test_adjust_timescale)
            #            .pipe(lambda df: df if print(df) else df)
        )

        return df

    def test_adjust_timescale(self, df: pd.DataFrame) -> None:
        """
        test whether adjust_timescale resulted in all unique time values. Assumes that
        all time observation points for a sample start off as unique values, and have
        millisecond granularity.
        TODO:
        - [ ] add test dataset that is more precise (will fail this test as the
        variance will be at a lower scale than millisecond)
        """
        size = (
            df.stack(["samplecode", "wine"])
            .groupby(["samplecode", "wine", "mins"])
            .size()
            .where(lambda s: s > 1)
            .dropna()
            .size
        )

        assert size == 0, f"expected size 0, instead {size}"
        return df

    def correct_offset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Refer to
        [Determining Time Axis Offset](notebooks/determining_time_axis_offset.ipynb).
        All chromatograms contain a scalar offset determined by the value of the first
        time point. A simple subtraction of that value from all time values of that
        sample centers the sample so that the first time point is zero, and all sample
        time axes are equal (for a given length and frequency).
        """
        df = (
            df.pipe(self.validate_dataframe)
            .stack(["samplecode", "wine"])
            .assign(
                mins=lambda df: df.groupby(["samplecode", "wine"])["mins"].transform(
                    lambda x: x - x.iloc[0]
                )
            )  # adjust time axis by initial value so they all start at 1
            .unstack(["samplecode", "wine"])
            .reorder_levels(["samplecode", "wine", "vars"], axis=1)
            .sort_index(level=0, axis=1, sort_remaining=True)
            .pipe(self.validate_dataframe)
            .pipe(self.test_correct_offset)
        )
        return df

    def test_correct_offset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Refer to
        [Determining Time Axis Offset](notebooks/determining_time_axis_offset.ipynb).
        Tests whether `self.correct_offset` results in the same time value for a given
        observation by observing the number of unique values in a given row. If
        num_unique > 1 (given by groupby size where groupby is on the row index) fails.


        """
        # test whether all first values are 0, i.e. offest is corrected. There is no
        # convievable way that this would fail as x-x is always 0, however its a good
        # redundancy
        (
            df.stack(["samplecode", "wine"])
            .groupby(["samplecode", "wine"])["mins"]
            .first()
            .pipe(
                lambda s: pd.testing.assert_series_equal(
                    left=s,
                    right=pd.Series(
                        [0] * len(s),
                        index=s.index,
                        dtype="timedelta64[ns]",
                        name="mins",
                    ),
                )
            )
        )

        (
            df.pipe(self.validate_dataframe)
            .loc[:, pd.IndexSlice[:, :, "mins"]]
            .dropna()  # make all series the same length
            .agg([pd.unique], axis=1)  # get unique values in each row
            # .pipe(lambda s: s if print(s) else s)
            .explode(
                "unique"
            )  # expand on the index so each unique value per row now has multiple entries
            .groupby("i")  # groupby index to see how many unique elements per row index
            .size()
            .where(
                lambda s: s > 1
            )  # filter out any row indexes where more than 1 unique value. If false, returns NaN
            .dropna()  # remaining rows will be rows that had more than 1 unique value
            # .pipe(lambda s: s if print(s) else s)
            .pipe(
                lambda s: pd.testing.assert_series_equal(
                    s, pd.Series(dtype="float64").rename_axis("i")
                )
            )
        )
        return df

    def tidy_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        take a long format dataframe with at least 3 levels index matching the labels
        and returns it to tidy, or wide format. To be used at the end of pipes, esp.
        row-oriented groupbys. The reverse of `.long_format`
        """
        df = (
            df.unstack(["wine", "samplecode"])
            .reorder_levels(["samplecode", "wine", "vars"], axis=1)
            .sort_index(axis=1)
            .reindex(["mins", "value", "baseline", "value_bcorr"], level=2, axis=1)
        )

        return df

    def long_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        stack a multilevel column dataframe to prepare it for row-based groupbys and
        other operations. The opening move of all my pipeline operations. Reversed
        by `.tidy_format`.
        """
        df = df.stack(["samplecode", "wine"]).sort_index(level=["samplecode", "wine"])
        return df

    def subtract_baseline(self, df: pd.DataFrame) -> pd.DataFrame:
        def plot_baseline_correction(grp):
            fig, ax = plt.subplots(1)

            grp.plot(
                x="mins", y="value", ax=ax, title=grp.index.get_level_values("wine")[0]
            )
            grp.plot(x="mins", y="baseline", ax=ax)

            plt.show()
            return grp

        df = (
            df
            # .pipe(self.validate_dataframe)
            .pipe(self.long_format)
            .groupby(["samplecode", "wine"], as_index=False)
            .apply(
                lambda grp: grp.assign(
                    baseline=Baseline(grp["mins"].dt.total_seconds()).iasls(
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
