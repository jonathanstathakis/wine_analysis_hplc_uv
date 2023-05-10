import os
import sys
import duckdb as db
import pandas as pd
sys.path.append('../')
from agilette.modules.metadata_sampletracker_cellartracker_join import get_cellar_tracker_table
import numpy as np
from db_methods import display_table_info

def init_raw_cellartracker_table(con):

    cellartracker_df = get_cellar_tracker_table()

    table_name = 'raw_cellartracker'

    con.sql(f"DROP TABLE IF EXISTS {table_name}")

    con.sql(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM cellartracker_df")

    display_table_info(con, table_name)

def main():
    init_raw_cellartracker_table()

if __name__ == '__main__':
    main()

