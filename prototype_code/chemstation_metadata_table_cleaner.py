"""
Contain all the methods to clean the chemstation metadata table before input into super_table_pipe.

Acts on a local table which is written by prototype_code/chemstation_db_tables_metadata_data.py
"""
import pandas as pd 
import numpy as np
import duckdb as db
from df_cleaning_methods import df_string_cleaner
from db_methods import display_table_info, write_df_to_table

def init_cleaned_chemstation_metadata_table(con, raw_table_name):

    df = con.sql(f"SELECT notebook, date, method, path, sequence_name, hash_key FROM {raw_table_name}").df()
    
    df = df_string_cleaner(df)
    
    df = df.rename({'notebook' : 'id', 'date' : 'acq_date', 'method' : 'acq_method'}, axis = 1)

    #df = df.drop(axis = 1, [])
    
    df['acq_date'] = pd.to_datetime(df['acq_date']).dt.strftime("%Y-%m-%d")
    
    df = chemstation_id_cleaner(df)

    df = chemstation_metadata_drop_unwanted_runs(df)

    write_cleaned_chemstation_metadata_table(df, con, raw_table_name)

    return None

def chemstation_metadata_drop_unwanted_runs(df : pd.DataFrame) -> pd.DataFrame:
    
    df = df[~(df['new_id'] == 'coffee') \
            & ~(df['new_id'] == 'lor-ristretto') \
            & ~(df['new_id'] == 'espresso') \
            & ~(df['new_id'] == 'lor-ristretto_column-check') \
            & ~(df['new_id'] == 'nc1') \
            & ~(df['old_id'].isna())
             ]
    df = library_id_replacer(df)

    print("\nthe following new_id's are not digits and will cause an error when writing the table:\n")
    print(df[~(df['new_id'].str.isdigit())])

    return df

def write_df_to_table_variables():
    
    schema = """
    old_id VARCHAR,
    acq_date DATE,
    acq_method VARCHAR,
    path VARCHAR,
    sequence_name VARCHAR,
    hash_key VARCHAR,
    new_id INTEGER
    """

    column_names = """
    old_id,
    acq_date,
    acq_method,
    path,
    sequence_name,
    hash_key,
    new_id
    """

    return schema, column_names, column_names


def four_digit_id_to_two_digit(df : pd.DataFrame) -> pd.DataFrame:
    df = df.rename({'id' : 'old_id'}, axis = 1)
    df['new_id'] = df['old_id'].astype(str).apply(lambda x : x[1:3] if len(x)==4 else x)
    return df

def string_id_to_digit(df : pd.DataFrame) -> pd.DataFrame:
    """
    Replaces the id of a number of runs with their 2 digit id's as stated in the sample tracker.
    """
    # 1. z3 to 00
    df['new_id'] = df['new_id'].replace({'z3':'00'})
    return df

def chemstation_id_cleaner(df : pd.DataFrame) -> pd.DataFrame:
    print("cleaning chemstation run id's")
    df = four_digit_id_to_two_digit(df)
    df = string_id_to_digit(df)
    return df

def library_id_replacer(df : pd.DataFrame) -> pd.DataFrame:
    replace_dict = {
        '2021-debortoli-cabernet-merlot_avantor|debertoli_cs': '72',
        'stoney-rise-pn_02-21' : '73',
        'crawford-cab_02-21' : '74',
        'hey-malbec_02-21' : '75',
        'koerner-nellucio-02-21' : '76'
                            }

    df['new_id'] = df['new_id'].replace(replace_dict, regex = True)

    return df

def write_cleaned_chemstation_metadata_table(df : pd.DataFrame, con : db.DuckDBPyConnection, raw_table_name : str) -> None:

    new_table_name = raw_table_name.replace('raw','cleaned')

    schema, table_column_names, df_column_names = write_df_to_table_variables()

    try:
        print(f"\nwriting df of shape {df.shape}, columns: {df.columns} to db\n")

        write_df_to_table(df, con, new_table_name, schema, table_column_names, df_column_names)
    except Exception  as e:
        print(f'Exception encountered when writing cleaned_chemstation_metadata_table to database: {e}')

def main():
    con =   db.connect('wine_auth_db.db')
    raw_table_name = 'raw_chemstation_metadata'
    init_cleaned_chemstation_metadata_table(con, raw_table_name)

if __name__ == "__main__":
    main()