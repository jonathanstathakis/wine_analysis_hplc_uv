"""
Top level file to initialize a wine auth database from scratch.
"""
import os
import duckdb as db
import sys

sys.path.append('../')

from init_chemstation_data_metadata import init_raw_chemstation_tables
from init_raw_sample_tracker_table import init_raw_sample_tracker_table
from init_raw_cellartracker_table import init_raw_cellartracker_table

from chemstation_metadata_table_cleaner import init_cleaned_chemstation_metadata_table
from sample_tracker_cleaner import init_cleaned_sample_tracker_table
from cellartracker_cleaner import init_cleaned_cellartracker_table
from function_timer import timeit

@timeit
def initialize_db():

    table_name = 'wine_auth_db.db'
    data_lib_path = "/Users/jonathan/0_jono_data"

    # remove old db if it exists.
    if os.path.exists(table_name):
        os.remove(table_name)
        print(f"deleted {table_name}")

    con = db.connect(f'{table_name}')
    
    load_raw_tables(con, data_lib_path)
    
    load_cleaned_tables(con)

    con.sql('DESCRIBE').show()

def load_raw_tables(con, data_lib_path):
        init_raw_chemstation_tables(data_lib_path, con)
        init_raw_sample_tracker_table(con)
        init_raw_cellartracker_table(con)

def load_cleaned_tables(con):
    init_cleaned_chemstation_metadata_table(con, 'raw_chemstation_metadata')
    init_cleaned_sample_tracker_table(con, 'raw_sample_tracker')
    init_cleaned_cellartracker_table(con, 'raw_cellartracker')

def main():
    initialize_db()

if __name__ == "__main__":
    main()