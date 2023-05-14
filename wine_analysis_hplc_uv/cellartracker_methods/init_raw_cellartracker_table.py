import os
import sys

import duckdb as db
import numpy as np
import pandas as pd

from ..cellartracker_methods import download_cellartracker_table
from ..db_methods import db_methods


def init_raw_cellartracker_table(con):
    cellartracker_df = download_cellartracker_table.get_cellar_tracker_table()

    table_name = "raw_cellartracker"

    con.sql(f"DROP TABLE IF EXISTS {table_name}")

    con.sql(
        f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM cellartracker_df"
    )

    db_methods.display_table_info(con, table_name)


def main():
    init_raw_cellartracker_table()


if __name__ == "__main__":
    main()
