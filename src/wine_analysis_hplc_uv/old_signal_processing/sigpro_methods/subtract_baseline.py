"""
baseline subtraction
"""

import polars as pl
import numpy as np
from pybaselines import Baseline
from typing import Any


def subtract_baseline_from_samples(
    df: pl.DataFrame,
    x_data_col: str,
    data_col: str,
    group_col: str | list[str],
    asls_kwargs: dict = {},
) -> tuple[pl.DataFrame, dict[str, Any]]:
    """
    subtract a fitted baseline from `data_col`, adding the baseline subtracted and
    calculated baseline to the dataframe as output.

    This is a wrapper around `subtract_baseline_asls` for dataframes of stacked samples
    indexed by `group_col`. For a single frame, use `subtract_baseline_asls`.
    """
    baseline_subtracted_dfs = {}
    params = {}
    for key, grp in df.partition_by(by=group_col, as_dict=True).items():
        baseline_subtracted_dfs[key], params[key] = subtract_baseline_asls(
            df=grp, x_data_col=x_data_col, data_col=data_col, asls_kwargs=asls_kwargs
        )

    df_ = pl.concat(baseline_subtracted_dfs.values())

    return df_, params


def subtract_baseline_asls(
    df: pl.DataFrame,
    x_data_col: str,
    data_col: str,
    asls_kwargs: dict = {},
) -> tuple[pl.DataFrame, dict[str, Any]]:
    """
    For a single frame, fit a baseline to the values of `data_col`, subtract the baseline
    from `data_col`, then add both the baseline and corrected values to the output df.

    :param x_data_col: the sampling point data, generally the time array.
    :param data_col: the curve to be corrected, generally absorbance.
    """

    # Baseline expects numpy
    x = np.asarray(df.get_column(x_data_col), dtype=np.float64)
    y = np.asarray(df.get_column(data_col), dtype=np.float64)

    bobj = Baseline(x_data=x, assume_sorted=True)
    baseline, params = bobj.asls(y, **asls_kwargs)

    y_corr = y - baseline

    df = df.with_columns(pl.lit(baseline).cast(float).alias("baseline"))
    df = df.with_columns(pl.lit(y_corr).cast(float).alias("corrected"))

    return df, params
