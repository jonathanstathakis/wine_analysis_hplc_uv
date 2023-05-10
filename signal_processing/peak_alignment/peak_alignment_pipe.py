"""
~~rule: signal dataframes are always structured index | mins | signal~~
rule: dataframes with a combination of signal and metadata will always have the sample name as the index.
rule: use dictionaries to handle collections of dataframes.
rule: ditch time.

1. interpolate time axis, then just store 1 time array in a df. reduces dimensionality by 1.

"""

import sys
sys.path.append('../../wine_analysis_hplc_uv')
import duckdb as db
import pandas as pd
import numpy as np
import db_methods
import signal_data_treatment_methods as dt
import plotly_plot_methods
import streamlit as st
st.set_page_config(layout="wide")
import signal_alignment_methods as sa
from typing import Union, List
import pickle
import os
import shutil

#create your figure and get the figure object returned

def pickle_pipe_check(db_path : str, wavelength: Union[str, List[str]] = None, display_in_st : bool = False, pickle_dir_name : str = None):
    peak_alignment_pipe_pickle_dir_name = 'peak_alignment_pipe_pickle_jar'
    # test if pickle dir exists, if not, create it.
    if not os.path.isdir(f'{peak_alignment_pipe_pickle_dir_name}'):
        create_pipe_pickle = input('no peak alignment pipe pickle dir detected, create now? (y/n): ')
        if create_pipe_pickle == 'y':
            os.mkdir(f'{peak_alignment_pipe_pickle_dir_name}')
            print(f'pickle jar created at {peak_alignment_pipe_pickle_dir_name}')
        elif create_pipe_pickle == 'n':
            peak_alignment_pipe_pickle_dir_name = None
            df = peak_alignment_pipe(db_path, wavelength, pickle_path_prefix=peak_alignment_pipe_pickle_dir_name)
        else:
            print('bad input, try again.')

    if os.path.isdir(f'{peak_alignment_pipe_pickle_dir_name}'):
        use_prev_pickle = input('use previous peak alignment pipe pickle? (y/n): ')
        if use_prev_pickle == 'y':
            df = peak_alignment_pipe(db_path, wavelength, peak_alignment_pipe_pickle_dir_name)
        elif use_prev_pickle == 'n':
            shutil.rmtree(peak_alignment_pipe_pickle_dir_name)
            os.mkdir(peak_alignment_pipe_pickle_dir_name)
            df = peak_alignment_pipe(db_path, wavelength, pickle_path_prefix=peak_alignment_pipe_pickle_dir_name)
        else:
            print('bad input try again')

def rw_pipe_pickle(series: pd.Series, pickle_dir_path : str = None):
    """
    read and write a series of dataframes to store parts of the peak alignment pipe.
    """
    if pickle_dir_path == None:
        return
    
    filepath = os.path.join(pickle_dir_path, f"{series.name}.pk")
    
    if not os.path.isfile(filepath):
        print(f"{filepath} does not exist, creating pickle now")
        
        with open(filepath, 'wb') as f:
            pickle.dump(df, f)
    else:
        print(f'reading {filepath}')
        with open(filepath, 'rb') as f:
            df = pickle.load(f)
    return df






def peak_alignment_pipe(db_path : str, wavelength: Union[str, List[str]] = None, pickle_path_prefix : "str" = None):
    """
    A pipe to align a supplied library of chromatograms.
    """
    raw_signal_col_name = f'raw {wavelength}'
            
    con = db.connect(db_path)

    # get the library and 254 nm signal

    df = get_library(con, wavelength, raw_signal_col_name)

    st.subheader('Group Contents')
    st.write(df.drop(f'raw {wavelength}', axis = 1))

    # get raw matrices
    signal_df_series = df[raw_signal_col_name]
    st.header('raw signal')

    signal_df_series.pipe(peak_alignment_st_output)
    # subtract baseline. If baseline not subtracted, alignment WILL NOT work.
    signal_df_series = signal_df_series.pipe(sa.baseline_subtraction)
    signal_df_series.pipe(peak_alignment_st_output)
    signal_df_series = signal_df_series.pipe(dt.normalize_library_absorbance)
    signal_df_series.pipe(peak_alignment_st_output)
    signal_df_series = signal_df_series.pipe(sa.interpolate_chromatogram_times)
    signal_df_series.pipe(peak_alignment_st_output)
    
    # calculate correlations between chromatograms as pearson's r, identify sample with highest average correlation, store key as most represntative sample for downstream peak alignment.
    y_df = signal_df_series.pipe(sample_name_signal_df_builder)
    corr_df = y_df.corr()
    highest_corr_key = find_representative_sample(corr_df)

    signal_df_series.pipe(sa.peak_alignment, highest_corr_key)
    signal_df_series.pipe(peak_alignment_st_output)
    # # # align the library time axis with dtw
    # peak_aligned_series_name = f'aligned_{wavelength}'
    # df[peak_aligned_series_name] = sa.peak_alignment(df[time_interpolated_chromatogram_name], highest_corr_key)

    return df

def fetch_sample_dataframes_with_spectra(con : db. DuckDBPyConnection) -> None:
    with  con:
        query = """
        SELECT
            acq_date,
            new_id,
            vintage_ct,
            name_ct,
            varietal,
            hash_key
        FROM super_table
        WHERE
            super_table.hash_key LIKE '%ed669e74%'
            OR super_table.hash_key LIKE '%513fd979%'
            OR super_table.hash_key LIKE '%112f4287%'
            OR super_table.hash_key LIKE '%bf648dfb%'
            --OR super_table.hash_key LIKE '%9b7abe4e%'
        """
    
        df = con.sql(query).df()
        df = db_methods.get_spectra(df, con)
        
    return df

def get_library(con : db.DuckDBPyConnection, wavelength : str, signal_col_name : str) -> pd.DataFrame:
    # get the selected runs to build the library
    df = fetch_sample_dataframes_with_spectra(con)
    df = df.set_index('name_ct', drop = True)

    # select the 254nm wavelength column across the library
    
    df[signal_col_name] = dt.subset_spectra(df['spectra'], wavelength)
    df = df.drop('spectra', axis =1)

    return df


def sample_name_signal_df_builder(df_series : pd.Series):
    # extract the sample names as column names, y_axis column as column values.
    sample_name_signal_df = pd.DataFrame(columns = df_series.index)

    for idx, row in df_series.items():
       sample_name_signal_df[idx] = row.iloc[:,1]
    
    return sample_name_signal_df

def find_representative_sample(corr_df = pd.DataFrame) -> str:
    corr_df = corr_df.replace({1 : np.nan})
    corr_df['mean'] = corr_df.apply(np.mean)
    corr_df = corr_df.sort_values(by = 'mean', ascending=False)    
    highest_corr_key = corr_df['mean'].idxmax()

    st.header('spectrum correlation matrix')
    st.write(corr_df)
    st.subheader('average highest correlation value')
    st.write(corr_df['mean'])
    st.write(f"{corr_df['mean'].idxmax()} has the highest average correlation with {corr_df['mean'].max()}\n")

    return highest_corr_key

def peak_alignment_st_output(series : pd.Series
                              ) -> None:
    """
    Display the intermediate and final results of the the pipeline. As each stage of the pipeline is stored in the df as a column idx : wine, column : dfs, can iterate through the columns, using the col naems as section headers.
    """
    st.subheader(f'{series.name}')

    x_axis_name = list(series.iloc[0].columns)[0]
    y_axis_name = list(series.iloc[0].columns)[1]

    fig = plotly_plot_methods.plot_signal_in_series(series, x_axis_name, y_axis_name)

    st.plotly_chart(fig)

    return None

def main():

    pickle_filepath ="alignment_df_pickle.pk1"
    db_path = '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db'
    wavelength='254'
    #display_in_st=True

    pickle_pipe_check(db_path, wavelength, pickle_filepath)
    
if __name__ == '__main__':
    main()