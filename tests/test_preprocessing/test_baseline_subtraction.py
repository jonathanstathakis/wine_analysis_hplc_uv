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
def mock_df():
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
        .rename_axis("idx", axis=0)
        # .pipe(lambda df: df if print(df) is None else df)
    )


@pytest.fixture
def pwd(corecon):
    get_data.get_wine_data(con=corecon, wavelength=(200,), mins=(0, 1))
    df = pivot_wine_data.pivot_wine_data(corecon)
    idx = pd.IndexSlice
    df = df.loc[:, idx[:, :, ["mins", "value"]]]
    return df


def test_multiindex_level_0(pwd) -> None:
    """
    test whether name is 'samplecode'. as per level_1 test, lack of standardisation
    means its hard to right a robust test.
    """
    assert pwd.columns.names[0] == "samplecode"


def test_multiindex_level_1(pwd) -> None:
    """
    test whether name is 'wine'. Hard to conduct any further testing at this point due
    to lack of standardisation of wine name patterns. can develop later if nes.
    """
    assert pwd.columns.names[1] == "wine"


def test_multiindex_level_2(pwd) -> None:
    """
    Test level 2 multiindex by check members and repeated pattern of ['mins','value']
    """
    names = pwd.columns.names
    assert names[2] == "vars"

    # the pipe assumes that the vars index level follows pattern ['mins','value'], and
    # only contains those values (2023-08-22 11:56:49 this may change later)

    vars_values = pwd.columns.get_level_values("vars").to_list()
    pattern = ["mins", "value"]
    pat_len = len(pattern)
    assert len(vars_values) % pat_len == 0, "mismatched length of list"
    assert (
        pattern * (len(vars_values) // pat_len) == vars_values
    ), "incorrect pattern sequence"


def test_baseline_2(mock_df):
    """
    testing the method via groupby rather than vertical indexing
    """
    df = mock_df

    out = (
        df.stack(["samplecode", "wine"])
        .reset_index()
        .groupby(["samplecode", "wine"], as_index=False)
        .apply(
            lambda grp: grp.assign(
                baseline=Baseline(grp["mins"]).iasls(grp["value"])[0]
            )
        )
        .pivot(columns=["samplecode", "wine"], index="idx")
        .reorder_levels(["samplecode", "wine", "vars"], axis=1)
        .sort_index(axis=1)
        .reindex(["mins", "value", "baseline"], level=2, axis=1)
    )
    print(out)
    # out.loc[:, pd.IndexSlice[:, :, ["baseline", "value"]]].plot()
    # plt.show()

    assert False
