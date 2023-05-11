import duckdb
import pandas as pd
import numpy as np
import os
import polars as pl
from function_timer import timeit


@ft.timeit
def main():
    con = duckdb.connect("uv_database.db")
    query = "select * from metadata"

    metadata_df = con.execute(query).fetch_df()

    metadata_df["spectrum_join_prefix"] = "hplc_spectrum_"

    metadata_df["spectrum_key"] = metadata_df["spectrum_join_prefix"] + metadata_df[
        "hash_key"
    ].str.replace("-", "_")

    spectrum_table_name = metadata_df["spectrum_key"][0]

    query_2 = f"SELECT * from {spectrum_table_name}"

    df = con.execute(query_2).df()
    print(df)


if __name__ == "__main__":
    main()
