import sys
sys.path.append('../')
from agilette.modules.metadata_sampletracker_cellartracker_join import super_table_pipe
import duckdb as db
import pandas as pd
import db_methods as db_m
from function_timer import timeit
import numpy as np
import db_methods

@timeit
def load_super_table(con : db.DuckDBPyConnection):

    con.sql("drop table if exists super_table")

    chemstation_df = con.sql('SELECT * FROM cleaned_chemstation_metadata').df()
    sample_tracker_df = con.sql('SELECT * FROM cleaned_sample_tracker').df()
    cellartracker_df = con.sql('SELECT * FROM cleaned_cellartracker').df()

    cellartracker_df.vintage = cellartracker_df.vintage.astype('Int64')
    
    print(cellartracker_df[cellartracker_df['vintage'] == 'empty'])

    print(f'Starting with {chemstation_df.shape[0]} rows in chemstation_df')

    super_table_df = super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df)

    write_super_table_to_db(super_table_df, con)

def write_super_table_to_db(df : pd.DataFrame, con:db.DuckDBPyConnection) -> None:
    table_name = 'super_table'
    con.sql(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    db_methods.display_table_info(con, table_name)

def main():
    load_super_table()

if __name__ == "__main__":
    main()