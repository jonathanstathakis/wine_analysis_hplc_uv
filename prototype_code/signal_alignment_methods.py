"""
Various methods to align chromatograms prior to statistical analysis.

All methods will act on a provided series of df's, where the index is ideally the sample name.

Refer to prototype_code/peak_alignment.py for use of most of these methods (at date 2023-04-30).
"""
import pandas as pd
import numpy as np
import signal_data_treatment_methods as dt
from dtw import dtw

def baseline_subtraction(df_series: pd.Series, raw_signal_y_col_name : str, baseline_y_col_name : str):
    baselines = df_series.apply(lambda row : dt.calc_baseline(row, 'mins', raw_signal_y_col_name))
    baseline_subtracted_signals = {}

    for i in baselines.index:
        baseline_subtracted_signal = df_series.loc[i][raw_signal_y_col_name] - baselines.loc[i][baseline_y_col_name]
        baseline_subtracted_signals[i] = pd.DataFrame({ 'mins' : df_series.loc[i]['mins'], raw_signal_y_col_name : baseline_subtracted_signal})

    baseline_subtracted_signals_series = pd.Series(baseline_subtracted_signals)
    return baseline_subtracted_signals_series

def interpolate_chromatogram_times(df_series : pd.Series):
    """
    Change the core function to act on a single dataframe, then wrap in a loop.
    """
    # get range of time values
    max_time = 0
    min_time = 0

    max_time = max([val['mins'].max() for idx, val in df_series.items()])
    min_time = min([val['mins'].min() for idx, val in df_series.items()])

    print('interpolating common time axis across all input chromatograms:\n')
    print(f"min time point: {min_time}\n")
    print(f"max time point: {max_time}\n")

    time_points = np.linspace(start = min_time, stop = max_time, num = df_series.iloc[0]['mins'].shape[0])
    
    print("interpolated time series:\n")
    print(f"range: {min(time_points)} to {max(time_points)} with length {len(time_points)}")

    # Interpolate all chromatograms to the common set of time points
    interpolated_chromatograms_series = pd.Series()

    for row_name, row in df_series.items():
        interpolated_chromatogram_df = row.set_index('mins').reindex(time_points, method = 'nearest').interpolate().reset_index()
        interpolated_chromatograms_series[row_name] = interpolated_chromatogram_df

    return interpolated_chromatograms_series

def peak_alignment(chromatogram_df_series : pd.Series, highest_corr_key : str, wavelength : str):
    # Ensure that the data is the correct dtype
    chromatogram_df_series = chromatogram_df_series.apply(lambda row : row.astype(float))

    # Define reference chromatogram, convert to numpy array
    reference_chromatogram_np_array = chromatogram_df_series[highest_corr_key][wavelength].to_numpy()

    # Create new series to store aligned chromatograms
    aligned_chromatograms_series = pd.Series()

    for key, chromatogram_df in chromatogram_df_series.items():
        query_chromatogram_np_array = chromatogram_df[wavelength].to_numpy()

        # Calculate the DTW distance and path between the reference and current chromatogram
        alignment = dtw(query_chromatogram_np_array, reference_chromatogram_np_array, step_pattern='asymmetric', open_end=True, open_begin=True)

        # Align the current chromatogram to the reference chromatogram using the calculated path
        aligned_chromatogram_np_array = np.zeros_like(reference_chromatogram_np_array)

        for i, cur_idx in enumerate(alignment.index2):
            ref_idx = alignment.index1[i]
            aligned_chromatogram_np_array[cur_idx] = query_chromatogram_np_array[ref_idx]

        # Interpolate missing values in the aligned chromatogram
        valid_indices = np.where(aligned_chromatogram_np_array != 0)[0]
        if len(valid_indices) > 0:
            interp_func = np.interp(np.arange(len(aligned_chromatogram_np_array)), valid_indices, aligned_chromatogram_np_array[valid_indices])
        else:
            interp_func = aligned_chromatogram_np_array

        # Replace the original chromatogram with the aligned and interpolated chromatogram
        aligned_chromatogram_df = chromatogram_df.copy()
        aligned_chromatogram_df[wavelength] = interp_func
        aligned_chromatograms_series[key] = aligned_chromatogram_df
    
    return aligned_chromatograms_series
