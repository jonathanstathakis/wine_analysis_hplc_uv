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
from wine_analysis_hplc_uv.db_methods import pivot_wine_data, get_data
from pybaselines import Baseline
import matplotlib.pyplot as plt
import logging
from wine_analysis_hplc_uv.signal_processing.mindex_signal_processing import (
    SignalProcessor,
)

logger = logging.getLogger(__name__)

pd.options.display.width = None
pd.options.display.max_colwidth = 20
pd.options.display.max_rows = 20
pd.options.display.max_columns = 15
pd.options.display.colheader_justify = "left"

"""
rules:
1. level 0 must only have unique values
3. level 2 must only contain ['mins'],['value'], in that order.
"""


@pytest.fixture
def good_mock_df():
    return (
        pd.DataFrame(
            {
                ("100", "2000 wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("100", "2000 wine", "value"): [5, 10, 50, 100, 50, 10],
                ("200", "1998 wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("200", "1998 wine", "value"): [0, 100, 0, 25, 100, 10],
                ("201", "nv wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("201", "nv wine", "value"): [0, 100, 0, 25, 100, 10],
                ("500", "wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("500", "wine", "value"): [0, 100, 0, 25, 100, 10],
            }
        )
        .rename_axis(["samplecode", "wine", "vars"], axis=1)
        .rename_axis("i", axis=0)
        # .pipe(lambda df: df if print(df) is None else df)
    )


@pytest.fixture
def bad_mock_df():
    return (
        pd.DataFrame(
            {
                ("100", "2000 wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("100", "2000 wine", "value"): [5, 10, 50, 100, 50, 10],
                ("200", "1998 wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("200", "1998 wine", "value"): [0, 100, 0, 25, 100, 10],
                ("201", "nv wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("201", "nv wine", "value"): [0, 100, 0, 25, 100, 10],
                ("201", "wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("201", "wine", "value"): [0, 100, 0, 25, 100, 10],
            }
        )
        .rename_axis(["samplecode", "wine", "vars"], axis=1)
        .rename_axis("i", axis=0)
        # .pipe(lambda df: df if print(df) is None else df)
    )


def test_mock_df(mock_df):
    index_frame = mock_df.columns.to_frame().reset_index(drop=True)

    print(mock_df.iloc[:, :4])
    with pd.option_context("display.multi_sparse", False):
        print(mock_df.iloc[:, :4])

    # print(index_frame)
    assert False


@pytest.fixture
def pwd(corecon):
    get_data.get_wine_data(
        con=corecon,
        # detection=("cuprac",),
        # varietal=("shiraz",),
        samplecode=("116",),
        wavelength=(450,),
        mins=(0, 30),
    )
    df = pivot_wine_data.pivot_wine_data(corecon)
    idx = pd.IndexSlice
    df = df.loc[:, idx[:, :, ["mins", "value"]]]
    return df


@pytest.fixture
def signalprocessor():
    return SignalProcessor()


def test_validate_dataframe(signalprocessor, good_mock_df: pd.DataFrame) -> None:
    signalprocessor.validate_dataframe(good_mock_df)


def test_baseline(pwd):
    """
    testing the method via groupby rather than vertical indexing
    """
    df = pwd

    df.pipe(check_dataframe_props)

    out = (
        df.stack(["samplecode", "wine"])
        .reset_index()
        .groupby(["samplecode", "wine"], as_index=False)
        .apply(
            lambda grp: grp.assign(
                baseline=Baseline(grp["mins"]).iasls(grp["value"])[0]
            )
        )
        .groupby(["samplecode", "wine"], as_index=False)
        .apply(lambda grp: grp.assign(value_bcorr=grp["value"] - grp["baseline"]))
        .pivot(columns=["samplecode", "wine"], index="i")
        .reorder_levels(["samplecode", "wine", "vars"], axis=1)
        .sort_index(axis=1)
        .reindex(["mins", "value", "baseline", "value_bcorr"], level=2, axis=1)
    )
    print(out)
    # out.loc[:, pd.IndexSlice["154", :, ["value", "baseline"]]].plot()
    # plt.show()

    assert False
