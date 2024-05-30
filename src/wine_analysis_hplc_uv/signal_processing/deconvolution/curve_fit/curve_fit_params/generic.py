import polars as pl


def add_param_order_col(df: pl.DataFrame) -> pl.DataFrame:
    """
    add a `param_order` col containing an int value corresponding to the order of the parameters in the downstream bounds table: amp: 0, loc: 1, scale: 2, skew: 3.
    """
    param = df.select(pl.col("param").first()).item()

    if param == "amp":
        order = 0
    elif param == "loc":
        order = 1
    elif param == "scale":
        order = 2
    elif param == "skew":
        order = 3

    out = df.with_columns(pl.lit(order).alias("param_order"))

    return out
