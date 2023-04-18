import os
import sys
import duckdb as db
import pandas as pd
sys.path.append('../')
from agilette.modules.metadata_sampletracker_cellartracker_join import sample_tracker_df_builder
from duck_db_methods import write_table_from_df

def replace_sample_tracker_table():
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

    # download the current sample tracker table
    sample_tracker_df_dl = sample_tracker_df_builder()
    # replace empty strings
    sample_tracker_df_dl = sample_tracker_df_dl.replace({"" : None})
    
    # establish a database connection
    con = db.connect('uv_database.db')
    
    # check if sample_tracker table exists in db, if not, create and populate from sample_tracker_df_dl
    write_table_from_df(sample_tracker_df_dl, con, 'sample_tracker', schema, target_columns, column_assignment)

    con.sql("DESCRIBE TABLE sample_tracker").show()
    con.sql("SELECT COUNT(*) FROM sample_tracker").show()
    
    tail = con.sql("SELECT * FROM sample_tracker ORDER BY id DESC LIMIT 10")
    con.sql("SELECT ALL * from tail order by id").show()

if __name__ == '__main__':
    replace_sample_tracker_table()
