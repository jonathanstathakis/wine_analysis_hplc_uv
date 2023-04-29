"""
~~rule: signal dataframes are always structured index | mins | signal~~
rule: dataframes with a combination of signal and metadata will always have the sample name as the index.
rule: use dictionaries to handle collections of dataframes.
rule: ditch time.

1. interpolate time axis, then just store 1 time array in a df. reduces dimensionality by 1.
"""

import sys
import duckdb as db
sys.path.append('../../wine_analysis_hplc_uv')
import pandas as pd
import numpy as np
from dtw import dtw
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from prototype_code import db_methods
from prototype_code import signal_data_treatment_methods as dt
from prototype_code import plot_methods
import function_timer
import streamlit as st

def peak_alignment_pipe():
    con = db.connect('/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db')

    wavelength = '254'
    df = fetch_repres_spectra(con)
    single_nm_df = extract_single_wavelength(df, wavelength)
    single_nm_df = single_nm_df.set_index('name_ct', drop = True)
    single_nm_df = single_nm_df.drop('spectrum', axis =1)

    # subtract baseline
    # show signals before processing
    fig = plot_methods.plot_signal_in_series(single_nm_df, '254','mins','254')
    st.subheader('raw chromatograms')
    st.plotly_chart(fig)

    baseline_subtracted_df_col_name = 'baseline_subtracted_signals'
    single_nm_df[baseline_subtracted_df_col_name] = baseline_correction(single_nm_df, wavelength, '254','254')

    fig = plot_methods.plot_signal_in_series(single_nm_df, baseline_subtracted_df_col_name,'mins','254')
    st.subheader('baseline subtracted')
    st.plotly_chart(fig)

    single_nm_df_dict = single_nm_df_dict_builder(single_nm_df, baseline_subtracted_df_col_name)
    # fig = plot_methods.plot_signal_in_series(single_nm_df, 'baseline_subtracted_signals', 'mins','signal')
    # fig.show()

    y_df = sample_name_signal_df_builder(single_nm_df, baseline_subtracted_df_col_name)
    corr_df = y_df.corr()
    highest_corr_key = find_representative_sample(corr_df)
    
    interpolated_chromatogram_dict = interpolate_chromatogram_time(single_nm_df_dict)

    fig = plot_methods.plot_signal_from_df_in_dict(interpolated_chromatogram_dict, 'mins','254')
    st.subheader('time axis interpolated')
    st.plotly_chart(fig)

    peak_alignment(interpolated_chromatogram_dict, highest_corr_key, wavelength)

    return None

def baseline_correction(df: pd.DataFrame, col_name : str, raw_signal_y_col_name : str, baseline_y_col_name : str):
    baselines = df.apply(lambda row : dt.calc_baseline(row[col_name], 'mins', raw_signal_y_col_name), axis = 1)
    baseline_subtracted_signals = {}

    for i in baselines.index:
        baseline_subtracted_signal = df.loc[i][col_name][raw_signal_y_col_name] - baselines.loc[i][baseline_y_col_name]
        baseline_subtracted_signals[i] = pd.DataFrame({ 'mins' : df.loc[i][col_name]['mins'], raw_signal_y_col_name : baseline_subtracted_signal})

    baseline_subtracted_signals_series = pd.Series(baseline_subtracted_signals)
    return baseline_subtracted_signals_series

def interpolate_chromatogram_time(df_dict : dict):

    interpolated_df_dict = {}

    # get range of time values
    min_time = min([df_dict[key]['mins'].min() for key in df_dict.keys()])
    max_time = max([df_dict[key]['mins'].max() for key in df_dict.keys()])

    print('interpolating common time axis across all input chromatograms:\n')
    print(f"min time point: {min_time}\n")
    print(f"max time point: {max_time}\n")

    time_points = np.linspace(start = min_time, stop = max_time, num = df_dict[list(df_dict.keys())[0]].shape[0])
    
    print("interpolated time series:\n")
    print(f"range: {min(time_points)} to {max(time_points)} with length {len(time_points)}")

    # Interpolate all chromatograms to the common set of time points
    interpolated_chromatograms_dict = {}

    for key, chromatogram_df in df_dict.items():
        
        chromatogram_df['mins'] = chromatogram_df['mins'].fillna(0)
        interpolated_chromatogram = chromatogram_df.set_index('mins').reindex(time_points, method = 'nearest').interpolate().reset_index()
        interpolated_chromatograms_dict[key] = interpolated_chromatogram

    return interpolated_chromatograms_dict


def single_nm_df_dict_builder(single_nm_df, df_col_name):
    
    single_nm_df_dict = {}

    for idx, row in single_nm_df.iterrows():
        single_nm_df_dict[idx] = row[df_col_name]

    return single_nm_df_dict

def sample_name_signal_df_builder(single_nm_df, col_name : str):
    # extract the sample names as column names, y_axis column as column values.
    sample_name_signal_df = pd.DataFrame(columns = single_nm_df.index)

    for idx, row in single_nm_df.iterrows():
        print(idx)
        sample_name_signal_df[idx] = row[col_name]['254'].values
    
    return sample_name_signal_df

def fetch_repres_spectra(con : db. DuckDBPyConnection) -> None:
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
        df = db_methods.get_spectrums(df, con)
        
    return df

def extract_single_wavelength(single_wavelength_df : pd.DataFrame, wavelength : str) -> pd.DataFrame:

    def get_wavelength(spectrum_df : pd.DataFrame, wavelength) -> pd.DataFrame:
        spectrum_df = spectrum_df.set_index('mins')
        single_wavelength_df = spectrum_df[wavelength]
        single_wavelength_df = single_wavelength_df.to_frame().reset_index()

        return single_wavelength_df
    
    single_wavelength_df[wavelength] = pd.Series(single_wavelength_df.apply(lambda row : 
    get_wavelength(row['spectrum'], wavelength), axis = 1),index = single_wavelength_df.index)

    single_wavelength_df['signal_shape'] = single_wavelength_df.apply(lambda row : row[wavelength].shape, axis = 1)
    single_wavelength_df['signal_index'] = single_wavelength_df.apply(lambda row : row[wavelength].index, axis = 1)
    single_wavelength_df['signal_columns'] = single_wavelength_df.apply(lambda row : row[wavelength].columns, axis = 1)

    return single_wavelength_df

def find_representative_sample(corr_df = pd.DataFrame) -> str:

    corr_df['mean'] = corr_df.apply(np.mean)
    corr_df = corr_df.sort_values(by = 'mean', ascending=False)
    
    highest_corr_key = corr_df['mean'].idxmax()

    print(corr_df['mean'])

    print(f"{corr_df['mean'].idxmax()} has the highest average correlation with {corr_df['mean'].max()}\n")

    return highest_corr_key

def peak_alignment(chromatograms_dict, highest_corr_key, wavelength):
    # Ensure that the data is the correct dtype
    chromatograms_dict = {key: df.astype('float64') for key, df in chromatograms_dict.items()}

    # Define reference chromatogram, convert to numpy array
    reference_chromatogram_np_array = chromatograms_dict[highest_corr_key][wavelength].to_numpy()

    # Create new dict to store aligned chromatograms
    aligned_chromatograms_dict = {}

    for key, chromatogram_df in chromatograms_dict.items():
        query_chromatogram_np_array = chromatogram_df[wavelength].to_numpy()

        # Calculate the DTW distance and path between the reference and current chromatogram
        alignment = dtw(query_chromatogram_np_array, reference_chromatogram_np_array, step_pattern='asymmetric', open_end=True, open_begin=True)

        import matplotlib.pyplot as plt
        
        # warping function
        # plt.plot(alignment.index1, alignment.index2)
        # plt.show()

        fig, ax = plt.subplots()
        ax.plot(reference_chromatogram_np_array, 'r')
        #ax.text(0.0, 1.0, 'reference')
        ax.plot(alignment.index2,query_chromatogram_np_array[alignment.index1])
        ax.text(4000, 12.0, key)
        st.pyplot(fig)
        # Align the current chromatogram to the reference chromatogram using the calculated path
        # aligned_chromatogram_np_array = np.zeros_like(reference_chromatogram_np_array)

        # for cur_idx in range(len(chromatogram_signal_np_array)):
        #     ref_idx = alignment.loc[cur_idx, 'index1']
        #     aligned_chromatogram_np_array[cur_idx] = reference_chromatogram_np_array[ref_idx]

        # # Add the aligned chromatogram to the aligned_chromatograms DataFrame
        # aligned_chromatograms_dict[key] = aligned_chromatogram_np_array

    return aligned_chromatograms_dict


def plot_signals(df : pd.DataFrame) -> go.Figure:
    """
    Take a dataframe of columns of signals and produce an overlaid line plot.
    """
    fig = go.Figure()
    
    for col in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col, text=col))

    return fig

def main():
    peak_alignment_pipe()
    
if __name__ == '__main__':
    main()