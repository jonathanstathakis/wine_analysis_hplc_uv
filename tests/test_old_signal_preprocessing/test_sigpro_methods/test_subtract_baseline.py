"""
test baseline subtraction methods using the PyBaselines package
"""

import pytest
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods import subtract_baseline
import polars as pl
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Any


@pytest.fixture(scope="module")
def baseline_correction_results(
    test_data_l: pl.DataFrame,
) -> tuple[pl.DataFrame, dict[str, Any]]:
    """
    get the results of baseline subtraction
    """
    df_, params = subtract_baseline.subtract_baseline_from_samples(
        df=test_data_l, x_data_col="mins", data_col="value", group_col="samplecode"
    )

    return df_, params


@pytest.fixture(scope="module")
def bcorr_df(
    baseline_correction_results: tuple[pl.DataFrame, dict[str, Any]],
) -> pl.DataFrame:
    """
    the df containing the baseline correction results
    """
    return baseline_correction_results[0]


@pytest.fixture(scope="module")
def unique_samples(test_data_l: pl.DataFrame) -> list:
    """
    a list of unique samples in the input df
    """
    unique_samples = test_data_l.unique("samplecode").get_column("samplecode").to_list()

    return unique_samples


@pytest.fixture(scope="module")
def params(
    baseline_correction_results: tuple[pl.DataFrame, dict[str, Any]],
) -> dict[str, Any]:
    """
    The dict containing the baseline correction parameter information
    """
    return baseline_correction_results[1]


def test_baseline_subtraction_returns_polars_df(bcorr_df: pl.DataFrame) -> None:
    """
    test if execution works and whether the AUC is different, whether the dict has the same unique keys as the input df
    """

    assert isinstance(bcorr_df, pl.DataFrame)


@pytest.fixture(scope="module")
def y_data_col() -> str:
    """
    the string key to the input signal column
    """

    return "value"


@pytest.fixture(scope="module")
def corrected_col() -> str:
    """
    the string key to the corrected signal column
    """

    return "corrected"


@pytest.fixture
def input_auc(test_data_l: pl.DataFrame, y_data_col: str) -> float:
    """
    calculate the AUC of the input signal
    """

    y_data = test_data_l.get_column(y_data_col).to_numpy()
    auc = np.trapz(y=y_data)
    return auc


@pytest.fixture
def corrected_auc(bcorr_df: pl.DataFrame, corrected_col: str) -> float:
    """
    calculate the AUC of the input signal
    """

    y_data = bcorr_df.get_column(corrected_col).to_numpy()
    auc = np.trapz(y=y_data)
    return auc


def test_bcorr_auc_lt_input_auc(input_auc: float, corrected_auc: float) -> None:
    """
    assert that the input auc is greater than the corrected auc. For the chromatographic
    datasets, we expect baseline correction to always reduce auc.
    """
    assert input_auc > corrected_auc


def test_param_keys_match_input_samples(
    unique_samples: list, params: dict[str, Any]
) -> None:
    """
    match the param keys against the unique samples, error if mismatch
    """

    assert sorted(unique_samples) == sorted(list(params.keys()))


def plot_result(df: pl.DataFrame) -> None:
    """
    display the baseline correction result across the samples
    """

    # melt the signal columns so we can iterate over a column 'signal'
    df_melt = df.melt(
        id_vars=["i", "samplecode", "wine", "mins"],
        value_vars=["value", "baseline", "corrected"],
        variable_name="signal",
        value_name="abs",
    )

    sns.relplot(
        data=df_melt, x="mins", y="abs", hue="signal", col="samplecode", kind="line"
    )

    plt.show()
