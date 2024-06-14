import polars as pl


def to_enum(df: pl.DataFrame, col: str):
    """
    cast a column to Enum
    """
    enum_dtype = pl.Enum(df.get_column(col).unique().sort().cast(str))
    df_ = df.with_columns(pl.col(col).cast(str).cast(enum_dtype))
    return df_
