"""
test signal processing smoothing functions
"""

import pytest
import polars as pl
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods import smooth
from typing import Any, Literal


@pytest.fixture(scope="module")
def group_col() -> str:
    """
    the grouping col
    """
    return "samplecode"


@pytest.fixture(scope="module")
def value_col() -> str:
    """
    the grouping col
    """
    return "value"


@pytest.fixture(scope="module")
def smoothed_df(
    test_data_l: pl.DataFrame,
    group_col: str,
    value_col: str,
    savgol_kwargs: dict[str, Any],
) -> pl.DataFrame:
    """
    A dataframe containing the smoothed data
    """
    df_ = smooth.savgol_smooth_samples(
        df=test_data_l,
        group_col=group_col,
        value_col=value_col,
        savgol_kwargs=savgol_kwargs,
    )
    return df_


@pytest.fixture(scope="module")
def savgol_kwargs() -> dict[str, Any]:
    """
    the input parameters for `scipy.signal.savgol_filter`
    """
    return {"window_length": 1000, "polyorder": 2}


def calc_smoothness(
    df: pl.DataFrame,
    group_col: str,
    value_col: str,
    method: Literal["stddev", "deriv"] = "stddev",
) -> pl.DataFrame:
    """
    calculate the group-wise signal smoothness as the absolute sum of the foreward discrete difference

    Methods of calculating smoothness:

        1. sum of absolute foreward discrete difference[^1]
        2. sum of standard deviation in time order[^2]

    [^1]: https://dsp.stackexchange.com/questions/46267/how-to-measure-the-smoothness-of-a-signal
    [^2]: https://www.reddit.com/r/Python/comments/3lmc30/comment/cv7f6zb/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
    """
    match method:
        case "stddev":
            smoothness = _smoothness_as_std_dev(
                df=df, value_col=value_col, group_col=group_col
            )
        case "deriv":
            smoothness = _smoothness_as_disc_diff(
                df=df, value_col=value_col, group_col=group_col
            )

    return smoothness.sort(group_col)


def _smoothness_as_std_dev(
    df: pl.DataFrame, value_col: str, group_col: str
) -> pl.DataFrame:
    """
    smoothness as standard deviation
    """

    smoothness = df.groupby(group_col).agg(pl.col(value_col).std())

    return smoothness


def _smoothness_as_disc_diff(
    df: pl.DataFrame, value_col: str, group_col: str
) -> pl.DataFrame:
    """
    smoothness as discrete difference
    """
    smoothness = df.groupby(group_col).agg(pl.col(value_col).diff().abs().sum())

    return smoothness


@pytest.fixture
def input_signal_smoothness(
    test_data_l: pl.DataFrame,
    group_col: str,
    value_col,
    method: Literal["stddev"] = "stddev",
) -> pl.DataFrame:
    """
    group-wise smoothness, before savgol smoothing.
    """

    smoothness = calc_smoothness(
        df=test_data_l, group_col=group_col, value_col=value_col, method=method
    )

    return smoothness


@pytest.fixture
def smoothed_signal_smoothness(
    smoothed_df: pl.DataFrame,
    group_col: str,
    value_col: str,
    method: Literal["stddev"] = "stddev",
) -> pl.DataFrame:
    """
    group-wise smoothness after savgol smoothing.
    """

    smoothness = calc_smoothness(
        df=smoothed_df,
        group_col=group_col,
        value_col=value_col,
        method=method,
    )

    return smoothness


def test_savgol_smooth(
    input_signal_smoothness: pl.DataFrame,
    smoothed_signal_smoothness: pl.DataFrame,
) -> None:
    """
    test the effect of savitzy-golay smoothing on the dataset as applying the same smoothing to all
    samples in a long frame.

    smoothness will be measured as the sum of the foreward discrete difference
    """
    print(input_signal_smoothness)
    print(smoothed_signal_smoothness)
    assert input_signal_smoothness > smoothed_signal_smoothness
