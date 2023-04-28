""" 
A file to contain general duckdb database methods.
"""
import pandas as pd
import duckdb as db

def index():
    display_table_info()
    write_df_to_table()
    #list_table_names_not_spectrum()
    get_spectrums()

def display_table_info(con : db.DuckDBPyConnection, table_name : str) -> None:
    print(f"\n\n###### {table_name.upper()} TABLE ######\n")
    con.sql(f"DESCRIBE TABLE {table_name}").show()
    con.sql(f"SELECT COUNT(*) FROM {table_name}").show()
    con.sql(f"SELECT * FROM {table_name} LIMIT 5").show()
    return None

def write_df_to_table(df : pd.DataFrame, con : db.DuckDBPyConnection, table_name : str, schema : str, table_column_names : str, df_column_names : str) -> None:

    try:
        con.sql(f"""
        DROP TABLE IF EXISTS {table_name};
        CREATE TABLE {table_name} ({schema});
        """)
    except Exception as e:
        print(f'Exception encountered while trying to create new table {table_name}:{e}')
        
    insert_query = f"""
            INSERT INTO {table_name} (
            {table_column_names}
            )
            SELECT
            {df_column_names}
            FROM df;
            """
    try:
        con.sql(insert_query)
    except Exception as e:
        print(e)
        print(f"full query is:\n\n{insert_query}")
    
    display_table_info(con, table_name)

# def list_table_names_not_spectrum(con : db.DuckDBPyConnection) -> None:
#     query = """
#     SELECT table_name from information_schema.tables
#     WHERE table_type = 'BASE TABLE'
#     and table_name NOT LIKE '%hplc_spectrum%';
#     """
#     con.sql(query).show()

def get_spectrums(metadata_df : pd.DataFrame, con : db.DuckDBPyConnection) -> pd.DataFrame:
        """
        Pass a wine metadata dataframe with relevant hash_key to join to spectrums contained in spectrum table found through the con object. returns the metadata df with a spectrum column, where spectrums are nested dataframes.
        """
        def get_spectrum(con : db.DuckDBPyConnection, hash_key : str) -> pd.DataFrame:
            query = f"""
            SELECT * from spectrums
            where hash_key = '{hash_key}'
            """
            df = con.sql(query).df()
            return df

        metadata_df['spectrum'] = metadata_df.apply(lambda row : get_spectrum(con, row['hash_key']), axis = 1)
        metadata_df = metadata_df.drop('hash_key', axis =1)

        return metadata_df
