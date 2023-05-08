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
import plot_methods
import streamlit as st
st.set_page_config(layout="wide")
import signal_alignment_methods as sa
from typing import Union, List
import pickle
import os

#create your figure and get the figure object returned

def peak_alignment_pipe(db_path : str, wavelength: Union[str, List[str]] = None, display_in_st : bool = False):
    """
    A pipe to align a supplied library of chromatograms.
    """
    pickle_file_path = "alignment_df_pickle.pk1"
    selected_signal_col_name = f'raw {wavelength}'

    if not os.path.isfile(pickle_file_path):
            
        con = db.connect(db_path)

        # get the library and 254 nm signal

        df = get_library(con, wavelength, selected_signal_col_name)

        st.subheader('Group Contents')
        st.write(df.drop(f'raw {wavelength}', axis = 1))
        
        # subtract baseline. If baseline not subtracted, alignment WILL NOT work.
        baseline_subtracted_chromatogram_series_name = f'baseline_subtracted_{wavelength}'
        df[baseline_subtracted_chromatogram_series_name] = sa.baseline_subtraction(df[selected_signal_col_name], wavelength, wavelength)

        # time interpolation
        time_interpolated_chromatogram_name = f'time_interpolated_{wavelength}'
        df[time_interpolated_chromatogram_name] = sa.interpolate_chromatogram_times(df[baseline_subtracted_chromatogram_series_name])

        # calculate correlations between chromatograms as pearson's r, identify sample with highest average correlation, store key as most represntative sample for downstream peak alignment.
        y_df = sample_name_signal_df_builder(df[baseline_subtracted_chromatogram_series_name], wavelength)
        corr_df = y_df.corr()
        highest_corr_key = find_representative_sample(corr_df)

        # align the library time axis with dtw
        peak_aligned_series_name = f'aligned_{wavelength}'
        df[peak_aligned_series_name] = sa.peak_alignment(df[time_interpolated_chromatogram_name], highest_corr_key, 
        wavelength)
        
        with open(pickle_file_path, 'wb') as file:
            pickle.dump(df, file)
    else:
        with open(pickle_file_path, 'rb') as file:
            print('reading pickle')
            df = pickle.load(file)

    # show the results in a steamlit app
    if display_in_st == True:
        output_df = df.drop(['acq_date','new_id','vintage_ct','varietal'], axis = 1)
        peak_alignment_st_output(output_df)

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


def sample_name_signal_df_builder(df_series : pd.Series, y_col_name : str):
    # extract the sample names as column names, y_axis column as column values.
    sample_name_signal_df = pd.DataFrame(columns = df_series.index)

    for idx, row in df_series.items():
        sample_name_signal_df[idx] = row[y_col_name].values
    
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

def peak_alignment_st_output(df : pd.DataFrame
                              ) -> None:
    """
    Display the intermediate and final results of the the pipeline. As each stage of the pipeline is stored in the df as a column idx : wine, column : dfs, can iterate through the columns, using the col naems as section headers.
    """
    st.header("pipeline output")

    for colname, colval in df.items():
        
        st.subheader(f'{colname}')

        df_series = df[colname]
        x_axis_name = list(df_series.iloc[0].columns)[0]
        y_axis_name = list(df_series.iloc[0].columns)[1]

        fig = plot_methods.plot_signal_in_series(df_series, x_axis_name, y_axis_name)

        st.plotly_chart(fig)

    return None

def main():

    pickle_filepath ="alignment_df_pickle.pk1"

    if not os.path.isfile(pickle_filepath):
        peak_alignment_pipe(db_path = '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db', wavelength='254', display_in_st=True, pickle_filepath = pickle_filepath)
    
    use_pickle = input("use pickle? y/n:")
    
    if use_pickle == 'y':
        peak_alignment_pipe(db_path = '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db', wavelength='254', display_in_st=True, pickle_filepath = pickle_filepath)
    if use_pickle == 'n':
        os.remove(pickle_filepath)
        peak_alignment_pipe(db_path = '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db', wavelength='254', display_in_st=True, pickle_filepath = pickle_filepath)
    
if __name__ == '__main__':
    main()