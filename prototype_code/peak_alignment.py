"""
rule: signal dataframes are always structured index | mins | signal
rule: dataframes with a combination of signal and metadata will always have the sample name as the index.
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
    #fig.show()

    baselines = single_nm_df.apply(lambda row : dt.calc_baseline(row['254'], 'mins', '254'), axis = 1)

    baseline_subtracted_signals = {}

    for i in baselines.index:
        baseline_subtracted_signal = single_nm_df.loc[i]['254']['254'] - baselines.loc[i]['baseline_y']
        
        baseline_subtracted_signals[i] = pd.DataFrame({ 'mins' : single_nm_df.loc[i]['254']['mins'], 'signal' : baseline_subtracted_signal})

    baseline_subtracted_signals_series = pd.Series(baseline_subtracted_signals)

    single_nm_df['baseline_subtracted_signals'] = baseline_subtracted_signals_series

    # fig = plot_methods.plot_signal_in_series(single_nm_df, 'baseline_subtracted_signals', 'mins','signal')
    # fig.show()

    y_df = sample_name_signal_df_builder(single_nm_df)
    
    corr_df = y_df.corr()

    highest_corr_key = find_representative_sample(corr_df)

    single_nm_df_dict = single_nm_df_dict_builder(single_nm_df, wavelength)
    
    interpolated_chromatogram_dict = interpolate_chromatogram_time(single_nm_df_dict)

    fig = plot_methods.plot_signal_from_df_in_dict(interpolated_chromatogram_dict, 'mins','254')
    print(fig)
    fig.show()


#    peak_alignment(y_df, highest_corr_key)

    return None

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


def single_nm_df_dict_builder(single_nm_df, wavelength):
    
    single_nm_df_dict = {}

    for idx, row in single_nm_df.iterrows():
        single_nm_df_dict[idx] = row[wavelength]

    return single_nm_df_dict


def sample_name_signal_df_builder(single_nm_df):
    # extract the sample names as column names, y_axis column as column values.
    sample_name_signal_df = pd.DataFrame(columns = single_nm_df.index)

    for idx, row in single_nm_df.iterrows():
        print(idx)
        sample_name_signal_df[idx] = row['254']['254'].values
    
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

def peak_alignment(chromatograms, highest_corr_key):

    # ensure that the data is the corredt dtype
    chromatograms = chromatograms.astype('float64')

    # define reference chromatogram, convert to numpy array
    reference_chromatogram = chromatograms[highest_corr_key].to_numpy()

    # create container dataframe
    chromatograms = pd.DataFrame(index=chromatograms.index)

    print(chromatograms)

    for column in chromatograms.columns:
    
        chromatogram = chromatograms[column].to_numpy()

        # Calculate the DTW distance and path between the reference and current chromatogram
    
        alignment = dtw(reference_chromatogram, chromatogram, step_pattern='asymmetric', open_end=True, open_begin=True)

        # Align the current chromatogram to the reference chromatogram using the calculated path
        aligned_chromatogram = np.zeros_like(chromatogram)
        
        for i in range(len(alignment.index1)):
            ref_idx = alignment.index1[i]
            cur_idx = alignment.index2[i]
            aligned_chromatogram[cur_idx] = reference_chromatogram[ref_idx]

        # Add the aligned chromatogram to the aligned_chromatograms DataFrame
        chromatograms[column] = aligned_chromatogram

    #Plot the aligned chromatograms
    for column in chromatograms.columns:
        plt.plot(chromatograms[column], label=column)
    # plt.legend()
    #plt.show()

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

