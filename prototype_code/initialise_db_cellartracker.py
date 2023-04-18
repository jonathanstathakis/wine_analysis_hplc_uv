import os
import sys
import duckdb as db
import pandas as pd
sys.path.append('../')
from agilette.modules.metadata_sampletracker_cellartracker_join import get_cellar_tracker_table
import numpy as np
from duck_db_methods import write_table_from_df

def cellartracker_to_db():
    cellartracker_df = get_cellar_tracker_table()

    # replace nv with NaN
    cellartracker_df['vintage'] = cellartracker_df['vintage'].replace({'nv' : np.nan})

    schema = \
    """
    size VARCHAR,
    vintage INTEGER,
    name VARCHAR,
    locale VARCHAR,
    country VARCHAR,
    region VARCHAR,
    subregion VARCHAR,
    appellation VARCHAR,
    producer VARCHAR,
    type VARCHAR,
    color VARCHAR,
    category VARCHAR,
    varietal VARCHAR
    """

    target_columns = \
    """
    size,
    vintage,
    name,
    locale,
    country,
    region,
    subregion,
    appellation,
    producer,
    type,
    color,
    category,
    varietal
    """
    column_assignment = \
    """
    size,
    vintage,
    name,
    locale,
    country,
    region,
    subregion,
    appellation,
    producer,
    type,
    color,
    category,
    varietal
    """
    con = db.connect('uv_database.db')

    write_table_from_df(cellartracker_df, con, 'cellartracker', schema, target_columns, column_assignment)

    con.sql("DESCRIBE TABLE cellartracker").show()
    con.sql("SELECT COUNT(*) FROM cellartracker").show()

if __name__ == '__main__':
    cellartracker_to_db()

