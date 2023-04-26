import sys
sys.path.append('../')
from agilette.modules.metadata_sampletracker_cellartracker_join import super_table_pipe
import duckdb as db
import pandas as pd
import db_methods as db_m
from function_timer import timeit

@timeit
def db_super_pipe():
    with db.connect('wine_auth_db.db') as con:

        con.sql("drop table if exists super_table")

        chemstation_df = con.sql('SELECT * FROM cleaned_chemstation_metadata').df()

        sample_tracker_df = con.sql('SELECT * FROM cleaned_sample_tracker').df()

        cellartracker_df = con.sql('SELECT * FROM cleaned_cellartracker').df()

        print(f'Starting with {chemstation_df.shape[0]} rows in chemstation_df')

        super_table_df = super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df)

        create_super_table(super_table_df)

def create_super_table(df : pd.DataFrame, con:db.DuckDBPyConnection) -> None:
    con.sql("CREATE TABLE super_table AS SELECT * FROM super_table")

    con.sql("SELECT * FROM super_table").show()

def main():
    db_super_pipe()

if __name__ == "__main__":
    main()