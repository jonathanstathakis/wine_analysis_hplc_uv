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
import matplotlib.pyplot as plt
import db_methods
import signal_data_treatment_methods as dt
import plot_methods
import streamlit as st
import signal_alignment_methods as sa

def peak_alignment_pipe():
    con = db.connect('/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db')
    
    df = fetch_sample_dataframes_with_spectra(con)
    df = df.set_index('name_ct', drop = True)

    raw_chromatogram_series_name = 'raw_chromatograms'
    wavelength = '254'

    df[raw_chromatogram_series_name] = dt.subset_spectra(df['spectra'], wavelength)
    df = df.drop('spectra', axis =1)
    # subtract baseline. If baseline not subtracted, alignment WILL NOT work.
    
    baseline_subtracted_chromatogram_series_name = 'baseline_subtracted_signals'
    
    st.write(df[raw_chromatogram_series_name].columns)
    df[baseline_subtracted_chromatogram_series_name] = sa.baseline_subtraction(df[raw_chromatogram_series_name], wavelength, wavelength)

    time_interpolated_chromatogram_name = 'time_interpolated_chromatograms'
    df[time_interpolated_chromatogram_name] = sa.interpolate_chromatogram_times(df[baseline_subtracted_chromatogram_series_name])

    # calculate correlations between chromatograms as pearson's r, identify sample with highest average correlation, store key as most represntative sample for downstream peak alignment.
    y_df = sample_name_signal_df_builder(df[baseline_subtracted_chromatogram_series_name], wavelength)
    corr_df = y_df.corr()
    highest_corr_key = find_representative_sample(corr_df)

    peak_aligned_series_name = 'peak_aligned_chromatograms'
    df[peak_aligned_series_name] = sa.peak_alignment(df[time_interpolated_chromatogram_name], highest_corr_key, 
    wavelength)
    
    peak_alignment_st_output(df,
                             highest_corr_key,
                             wavelength,
                             raw_chromatogram_series_name,
                             baseline_subtracted_chromatogram_series_name,
                             time_interpolated_chromatogram_name,
                             peak_aligned_series_name)
    
    # change the code so that 'key' is the row name rather than dict key. Should be same same.

    return None

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

def peak_alignment_st_output(df : pd.DataFrame,
                              wavelength : str,
                              highest_corr_key : str, 
                              raw_chromatogram_series_name : str, baseline_subtracted_chromatogram_series_name : str, time_interpolated_chromatogram__series_name : str, peak_aligned_series_name : str
                              ) -> None:

    st.subheader('raw chromatograms')
    fig = plot_methods.plot_signal_in_series(df[raw_chromatogram_series_name],'mins','254')
    st.plotly_chart(fig)

    st.subheader('baseline subtracted')
    fig = plot_methods.plot_signal_in_series(df[baseline_subtracted_chromatogram_series_name],'mins','254')
    st.plotly_chart(fig)
    
    st.subheader('time interpolated chromatograms')
    fig = plot_methods.plot_signal_in_series(df[time_interpolated_chromatogram__series_name],'mins','254')
    st.plotly_chart(fig)

    st.subheader('aligned peak chromatograms')
    fig = plot_methods.plot_signal_in_series(df[peak_aligned_series_name],'mins','254')
    st.plotly_chart(fig)

    return None

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

def main():
    peak_alignment_pipe()
    
if __name__ == '__main__':
    main()