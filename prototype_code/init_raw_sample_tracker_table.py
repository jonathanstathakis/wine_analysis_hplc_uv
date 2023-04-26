import os
import sys
import pandas as pd
sys.path.append('../')
from agilette.modules.metadata_sampletracker_cellartracker_join import sample_tracker_df_builder
from db_methods import write_df_to_table
from db_methods import display_table_info

def init_raw_sample_tracker_table(con):
    # download the current sample tracker table
    df = sample_tracker_df_builder()

    # replace empty strings
    df = df.replace({"" : None})

    table_name = 'raw_sample_tracker'

    # establish a database connection
    write_raw_sample_tracker_table(df, con, table_name)
    display_table_info(con, table_name)


def write_raw_sample_tracker_table(df, con, table_name):
    schema = \
    """
        id INTEGER,
        vintage VARCHAR,
        name VARCHAR,
        open_date DATE,
        sampled_date DATE,
        added_to_cellartracker VARCHAR,
        notes VARCHAR,
        size INTEGER
    """

    target_columns = \
    """
        id,
        vintage,
        name,
        open_date,
        sampled_date,
        added_to_cellartracker,
        notes,
        size
    """

    column_assignment = target_columns

    write_df_to_table(df, con, table_name, schema, target_columns, column_assignment)

def main():
    init_raw_sample_tracker_table()
    
if __name__ == '__main__':
    main()
