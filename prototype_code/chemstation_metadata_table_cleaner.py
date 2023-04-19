"""
Contain all the methods to clean the chemstation metadata table before input into super_table_pipe.

Acts on a local table which is written by prototype_code/chemstation_db_tables_metadata_data.py
"""
import pandas as pd 
import numpy as np
import duckdb as db

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

def main():
    in_table_name = "raw_chemstation_metadata"
    out_table_name = "cleaned_chemstation_metadata"

    con = db.connect('uv_database.db')
    df = con.sql("SELECT * FROM raw_chemstation_metadata").df()

    df = df.rename({'notebook' : 'id', 'date' : 'acq_date', 'method' : 'acq_method'}, axis = 1)
    
    df['acq_date'] = pd.to_datetime(df['acq_date']).dt.strftime("%Y-%m-%d")

    df = chemstation_id_cleaner(df)
    
    
    df = df[~(df['new_id'] == 'coffee') \
            & ~(df['new_id'] == 'lor-ristretto') \
            & ~(df['new_id'] == 'espresso') \
            & ~(df['new_id'] == 'lor-ristretto_column-check') \
            & ~(df['new_id'] == 'nc1') \
            & ~(df['old_id'].isna())
             ]

    clean_df = library_id_replacer(df)

    print("\nthe following new_id's are not digits and will cause an error when writing the table:\n")

    print(clean_df[~(clean_df['new_id'].str.isdigit())])

    schema = """
    old_id VARCHAR,
    acq_date DATE,
    acq_method VARCHAR,
    unit VARCHAR,
    signal VARCHAR,
    path VARCHAR,
    sequence_name VARCHAR,
    hash_key VARCHAR,
    new_id INTEGER
    """

    con.sql(f"""
    DROP TABLE IF EXISTS {out_table_name};
    CREATE TABLE {out_table_name} ({schema});
    """)    
    
    con.sql(f"""
        INSERT INTO {out_table_name} (
        old_id,
        acq_date,
        acq_method,
        unit,
        signal,
        path,
        sequence_name,
        hash_key,
        new_id
        )
        SELECT
        old_id,
        acq_date,
        acq_method,
        unit,
        signal,
        path,
        sequence_name,
        hash_key,
        new_id
        FROM clean_df as df;
        """)

    print(f"\n## {out_table_name.upper()} ##\n")
    con.sql(f"DESCRIBE {out_table_name}").show()
    con.sql(f"SELECT COUNT(*) FROM {out_table_name}").show()

if __name__ == "__main__":
    main()