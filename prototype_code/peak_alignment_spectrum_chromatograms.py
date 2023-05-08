"""
Produce a pairwise euclidean distance matrix of sample sc matrices.

1. Get the samples and their sc matrices as a dataframe with 1 column of nested dataframes (the sc matrices). On the first run pickles the dataframe, then loads from the pickle for subsequent runs.
2. Construct the pairwise-distance matrix.
3. 
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
from function_timer import timeit
import pickle
import observing_spectra_shape_variation

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

@timeit
def peak_alignment_spectrum_chromatogram():
    
    # get a dataframe consisting of sample metadata and a column of sc matrices as nested dataframes.
    df = load_spectrum_chromatograms()
    df = df.drop('new_id', axis = 1)
    df = df.set_index('wine')

    df = observing_spectra_shape_variation.observe_sample_size_mismatch(df)
    df['normalized_matrix'] = normalize_library_absorbance(df['reshaped_matrix'])

    series = df['normalized_matrix']

    # subsetting series while testing code
    series = series[:5]

    for idx, tab in enumerate(st.tabs(list(series.keys()))):
        with tab:
            st.table(series[idx].describe())
    
    try:
        sim_df = sa.calculate_distance_matrix(series)
        st.table(sim_df)
    except Exception as e:
        print(e)

@timeit
def query_unique_wines_spectra_to_df(con : db.DuckDBPyConnection):
    print('starting')

    with  con:
        query = """
            SELECT ANY_VALUE(new_id) AS new_id, CONCAT(vintage_ct, ' ', name_ct) AS wine, ANY_VALUE(hash_key) AS hash_key, ANY_VALUE(path) AS path
            FROM super_table
            GROUP BY wine;
        """
        print('getting metadata_df')
        df = con.sql(query).df()
        print('getting spectra')

        df = db_methods.get_spectra(df, con)

    return df

@timeit
def normalize_library_absorbance(series : pd.Series) -> pd.Series:
    """
    Normalise a series of dataframes consisting of numeric values across the entire series, i.e. relative to each other. Returns a normalized series of dataframes.
    """

    import time
    start_time = time.time()

    def check_numeric_dataframes(series: pd.Series) -> bool:
        for df in series:
            non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_columns) > 0:
                return False
        return True

    if not check_numeric_dataframes(series):
        raise ValueError("All DataFrames in the series must consist of numeric values only.")


    end_time = time.time()
    time_taken = end_time - start_time
    print(f"time taken : {time_taken} seconds")
    
    # Find the global minimum and maximum values
    local_mins = series.apply(lambda df: df.min().min())
    local_maxs = series.apply(lambda df: df.max().max())
    
    global_min = local_mins.min()
    global_max = local_maxs.max()
    

    # Normalize each DataFrame in the series
    normalized_series = series.apply(
        lambda df: (df - global_min) / (global_max - global_min)
    )


    return normalized_series

@timeit
def write_unique_id_spectra_df(df : pd.DataFrame, filepath : str):
    print('writing pickle')
    with open(filepath, 'wb') as file:
        pickle.dump(df, file)
    return None

@timeit
def read_unique_id_spectra_pickle(filepath : str):
    print('reading pickle')
    with open(filepath, 'rb') as file:
        df = pickle.load(file)
    return df

@timeit
def load_spectrum_chromatograms():
    table_name = 'unique_new_id_spectra'
    filepath = table_name+'.pk1'

    # Check if the pickle file exists
    if not os.path.isfile(filepath):
        print('establishing conn. with db')
        db_path=os.environ.get('WINE_AUTH_DB_PATH')
        con = db.connect(db_path)        
        df = query_unique_wines_spectra_to_df(con)
        write_unique_id_spectra_df(df, filepath)

    else:
        df = read_unique_id_spectra_pickle(filepath)

    return df

@timeit
def main():
    peak_alignment_spectrum_chromatogram()

if __name__ == '__main__':
    main()