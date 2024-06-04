"""
Contain smoothing methods. There is a possible overlap with baseline subtraction
"""

from typing import Any
import polars as pl
from scipy import signal


def savgol_smooth_samples(
    df: pl.DataFrame,
    value_col: str,
    group_col: str | list[str],
    savgol_kwargs: dict[str, Any] = {},
) -> pl.DataFrame:
    """
    apply the same smoothing to each sample in the input frame
    """

    smoothed_samples: dict = {}
    for key, grp in df.partition_by(group_col, as_dict=True).items():
        x = grp.get_column(value_col).to_numpy()
        smoothed = signal.savgol_filter(x=x, **savgol_kwargs)
        smoothed_samples[key] = grp.with_columns(
            pl.lit(smoothed).cast(float).alias("smoothed")
        )

    df_ = pl.concat(smoothed_samples.values())
    return df_
