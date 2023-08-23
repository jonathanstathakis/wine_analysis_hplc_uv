"""
2023-08-21 20:30:37: a test module for baseline subtraction of a set of chromatographic
signals. The baseline modules are at this time for a peak alignment pipe located
[here](src/wine_analysis_hplc_uv/signal_processing/peak_alignment/peak_alignment_pipe.py)

TODO:

- [ ] establish a schema
- [ ] get test dataset
- [ ] establish metrics for measuring baseline subtraction change.
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

logger = logging.getLogger(__name__)

pd.options.display.width = None
pd.options.display.max_colwidth = 20
pd.options.display.max_rows = 20
pd.options.display.max_columns = 15
pd.options.display.colheader_justify = "left"

"""
rules:
1. level 0 must only have unique values
2. level 1 must match the regex '\d{4}|nv ..' (figure it out)
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


def check_dataframe_props(df: pd.DataFrame) -> None:
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
    assert df.columns.names[0] == "samplecode"
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

    return None


def test_check_dataframe_props(mock_df: pd.DataFrame) -> None:
    check_dataframe_props(mock_df)


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
