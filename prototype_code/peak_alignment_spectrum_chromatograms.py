"""
Produce a pairwise euclidean distance matrix of sample sc matrices.

1. Get the samples and their sc matrices as a dataframe with 1 column of nested dataframes (the sc matrices). On the first run pickles the dataframe, then loads from the pickle for subsequent runs.
2. Construct the pairwise-distance matrix.
"""
import df_methods
import sys
import os
import duckdb as db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import db_methods
import signal_data_treatment_methods as dt
import plot_methods
import streamlit as st
import signal_alignment_methods as sa
import function_timer
import pickle

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def peak_alignment_spectrum_chromatogram():
    
    df = load_spectrum_chromatograms()

def query_unique_wines_spectra_to_df(con : db.DuckDBPyConnection):
    print('starting')

    with  con:
        query = """
        SELECT new_id, ANY_VALUE(CONCAT(vintage_ct, ' ',name_ct)) AS wine, ANY_VALUE(hash_key) AS hash_key
        FROM super_table
        GROUP BY new_id;
        """
        print('getting metadata_df')
        metadata_df = con.sql(query).df()
        print('getting spectra')
    
        df = db_methods.get_spectra(metadata_df, con)

    return df

@function_timer.timeit
def write_unique_id_spectra_df(df : pd.DataFrame, filepath : str):
    print('writing pickle')
    with open(filepath, 'wb') as file:
        df.to_pickle(file)
    return None

@function_timer.timeit
def read_unique_id_spectra_pickle(filepath : str):
    print('reading pickle')
    df = pd.read_pickle(filepath)
    return df

def load_spectrum_chromatograms():
    table_name = 'unique_new_id_spectra'
    filepath = table_name+'.pk1'

    # Check if the table exists
    if not os.path.exists(filepath):
        print('establishing conn. with db')
        db_path=os.environ.get('WINE_AUTH_DB_PATH')
        con = db.connect(db_path)
        
        df = query_unique_wines_spectra_to_df(con)
        
        write_unique_id_spectra_df(df, filepath)

    else:
        df = read_unique_id_spectra_pickle(filepath)

    return df

@function_timer.timeit
def main():
    peak_alignment_spectrum_chromatogram()

if __name__ == '__main__':
    main()