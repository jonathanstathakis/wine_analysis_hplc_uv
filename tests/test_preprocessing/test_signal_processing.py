"""
2023-08-21 20:30:37: a test module for baseline subtraction of a set of chromatographic
signals. The baseline modules are at this time for a peak alignment pipe located
[here](src/wine_analysis_hplc_uv/signal_processing/peak_alignment/peak_alignment_pipe.py)

TODO:
- [ ] create a mock_df class initialized from a manually defined dict, then modify it
in class to fail variously defined tests, i.e. duplicated samplecodes, wrong order vars,
strings in column, not sorted mins, wrong order multiindex
"""

import pytest
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Index
import duckdb as db
import numpy as np
from wine_analysis_hplc_uv.db_methods import pivot_wine_data, get_data
from pybaselines import Baseline
import matplotlib.pyplot as plt
import logging
from . import preprocessing_test_dataset
from wine_analysis_hplc_uv.signal_processing.mindex_signal_processing import (
    SignalProcessor,
)

logger = logging.getLogger(__name__)

pd.options.display.width = None
# pd.options.display.max_colwidth = 20
pd.options.display.max_rows = 20
pd.options.display.max_columns = 15
pd.options.display.colheader_justify = "left"
import random

"""
rules:
1. level 0 must only have unique values
3. level 2 must only contain ['mins'],['value'], in that order.
"""


@pytest.fixture
def signalprocessor():
    return SignalProcessor()


@pytest.fixture()
def cupshz_dset(signalprocessor):
    df = preprocessing_test_dataset.test_dataset()
    df.pipe(signalprocessor.validate_dataframe)
    return df


def test_validate_dataframe(signalprocessor, cupshz_dset: pd.DataFrame) -> None:
    signalprocessor.validate_dataframe(cupshz_dset)


def test_cupshz_dset(cupshz_dset):
    assert not cupshz_dset.empty


def test_adjust_timescale(signalprocessor, cupshz_dset: pd.DataFrame) -> None:
    df = cupshz_dset.pipe(signalprocessor.adjust_timescale)


class BadDataSet:
    def __init__(self, df):
        self.base_dataset = df
        self.fail_offset = self.init_fail_offset()

    def init_fail_offset(self):
        """
        The each minute row of each sample is multiplied by a different random scalar to
        produce a highly irregular frequency, with the intent of failing
        `test_correct_offset`.
        """

        df = (
            self.base_dataset.stack(["samplecode", "wine"])
            .assign(
                mins=lambda df: df.groupby(["samplecode", "wine"])["mins"].transform(
                    lambda x: x * random.uniform(0, 1)
                )
            )
            .unstack(["samplecode", "wine"])
            .reorder_levels(["samplecode", "wine", "vars"], axis=1)
            .sort_index(axis=1)
        )
        return df


@pytest.fixture
def baddatasets(cupshz_dset):
    return BadDataSet(cupshz_dset)


def test_baddataset(baddatasets):
    print(baddatasets.fail_offset)
    assert False


def test_correct_offset(
    signalprocessor, cupshz_dset: pd.DataFrame, baddatasets
) -> None:
    # expect this to fail as they contain irregular frequency
    try:
        (
            baddatasets.fail_offset.pipe(signalprocessor.adjust_timescale).pipe(
                signalprocessor.correct_offset
            )
        )
    except AssertionError:
        pass

    # expect this to pass
    (
        cupshz_dset.pipe(signalprocessor.adjust_timescale).pipe(
            signalprocessor.correct_offset
        )
    )


# def test_baseline(pwd):
#     """
#     testing the method via groupby rather than vertical indexing
#     """
#     df = pwd

#     df.pipe(check_dataframe_props)

#     out = (
#         df.stack(["samplecode", "wine"])
#         .reset_index()
#         .groupby(["samplecode", "wine"], as_index=False)
#         .apply(
#             lambda grp: grp.assign(
#                 baseline=Baseline(grp["mins"]).iasls(grp["value"])[0]
#             )
#         )
#         .groupby(["samplecode", "wine"], as_index=False)
#         .apply(lambda grp: grp.assign(value_bcorr=grp["value"] - grp["baseline"]))
#         .pivot(columns=["samplecode", "wine"], index="i")
#         .reorder_levels(["samplecode", "wine", "vars"], axis=1)
#         .sort_index(axis=1)
#         .reindex(["mins", "value", "baseline", "value_bcorr"], level=2, axis=1)
#     )
#     print(out)
#     # out.loc[:, pd.IndexSlice["154", :, ["value", "baseline"]]].plot()
#     # plt.show()

#     assert False
