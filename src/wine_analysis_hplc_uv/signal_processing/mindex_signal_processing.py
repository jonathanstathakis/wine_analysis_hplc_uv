"""
2023-08-23 23:30:42

A module destined to replace [this one](./src/wine_analysis_hplc_uv/signal_processing/signal_data_treatment_methods.py). Primarily it differs in that it will have a class API, and expect a multiindexed dataframe as input.
"""

import pandas as pd
import logging

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
        ), "incorrect pattern sequence"

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
            .pipe(lambda df: df if print(df) else df)
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
            .pipe(lambda s: s if print(s) else s)
            .explode(
                "unique"
            )  # expand on the index so each unique value per row now has multiple entries
            .groupby("i")  # groupby index to see how many unique elements per row index
            .size()
            .where(
                lambda s: s > 1
            )  # filter out any row indexes where more than 1 unique value. If false, returns NaN
            .dropna()  # remaining rows will be rows that had more than 1 unique value
            .pipe(lambda s: s if print(s) else s)
            # .pipe(lambda s: pd.testing.assert_series_equal(s, pd.Series()))
        )
