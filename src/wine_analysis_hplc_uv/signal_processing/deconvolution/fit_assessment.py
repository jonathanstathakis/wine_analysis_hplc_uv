import numpy as np
import polars as pl
from wine_analysis_hplc_uv.signal_processing.deconvolution import types


def fit_assessment(
    df: pl.DataFrame,
    time_col: str,
    left_signal: str,
    right_signal: str,
) -> pl.DataFrame:
    """
    Take a single dataframe with two signal columns `left_signal`, `right_signal`, and a sampling interval time column `time_col` and compare their difference as the ratios AUC, specifically 1+AUC.
    """

    # calculate AUC ratio

    # calculate the AUCS + 1

    x = df[time_col]
    numerator = df[left_signal]
    denominator = df[right_signal]

    auc_ratio = _compute_auc_ratio(numerator=numerator, denominator=denominator, x=x)

    fit_report = pl.DataFrame({"auc_ratio": auc_ratio})
    return fit_report


def _compute_auc(
    x: types.FloatArray | pl.Series, y: types.FloatArray | pl.Series
) -> float:
    """
    compute the AUC of an input series `y` against time sampling points `x`. Return the AUC as a float
    """
    return np.trapz(x=x, y=y)


def _compute_auc_ratio(
    numerator: types.FloatArray | pl.Series,
    denominator: types.FloatArray | pl.Series,
    x: types.FloatArray | pl.Series,
) -> float:
    """
    calculate the ratio of 1+AUC for two input series, a `numerator`, and `denominator`. Return a float, the ratio.
    """

    auc_numerator = _compute_auc(x=x, y=numerator)
    auc_denominator = _compute_auc(x=x, y=denominator)
    auc_ratio = (1 + auc_numerator) / (1 + auc_denominator)

    return auc_ratio
