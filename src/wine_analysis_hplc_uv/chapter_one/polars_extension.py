import polars as pl
import numpy as np


def to_enum(df: pl.DataFrame, col: str):
    """
    cast a column to Enum
    """
    enum_dtype = pl.Enum(df.get_column(col).unique().sort().cast(str))
    df_ = df.with_columns(pl.col(col).cast(str).cast(enum_dtype))
    return df_


def calculate_auc_by_group(df: pl.DataFrame, grp_col: str, x_col: str, y_col: str):
    """
    Calculate the AUC of an input numerical column 'y_col' with an x component 'x_col'
    along groups labeled by 'grp_col'.

    Note: Compensates for signals with negative components by shift the signal to above zero
    before calculation
    """

    # check if negative values present in signal, and if so, shift
    if df.select(pl.col(y_col).lt(0).any()).item():
        df = df.with_columns(
            pl.col(y_col).sub(pl.col(y_col).min()).over(pl.col(grp_col)).alias(y_col)
        )

    # calculate auc
    aucs = (
        df.group_by(grp_col)
        .agg(
            pl.map_groups(
                [x_col, y_col], function=lambda x: np.trapz(x=x[0], y=x[1])
            ).alias("auc")
        )
        .sort([grp_col])
    )

    return aucs
