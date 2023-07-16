"""
2023-07-03 11:20:52

Defunct module, old implementation of downloading a local copy of my Cellar Tracker Cellar.
"""

import os
import sys

import duckdb as db
import numpy as np
import pandas as pd

from ..cellartracker_methods import download_cellartracker_table
from ..db_methods import db_methods


def init_raw_cellartracker_table(db_filepath: str, tbl_name: str) -> None:
    cellartracker_df = download_cellartracker_table.get_cellar_tracker_table()

    with db.connect(db_filepath) as con:
        con.sql(
            f"""
        DROP TABLE IF EXISTS
            {tbl_name}; 
        CREATE TABLE IF NOT EXISTS
            {tbl_name}
        AS SELECT
            *
        FROM
            cellartracker_df
            """
        )

    db_methods.display_table_info(db_filepath, tbl_name)

    return None


def main():
    init_raw_cellartracker_table()


if __name__ == "__main__":
    main()
