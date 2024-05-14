"""
Various methods to align chromatograms prior to statistical analysis.

All methods will act on a provided series of df's, where the index is ideally the sample name.

Refer to prototype_code/peak_alignment.py for use of most of these methods (at date 2023-04-30).
"""

from itertools import combinations

import numpy as np
import pandas as pd
from dtw import dtw
from scipy.spatial.distance import euclidean
from wine_analysis_hplc_uv.scripts.core_scripts import (
    signal_data_treatment_methods as dt,
)


def baseline_subtraction(df_series: pd.Series):
    print("calculating baselines..")
    x_col_key = "x"
    y_col_key = df_series.name
    df = df_series.to_frame().reset_index(names=[x_col_key])
    baselines = df.apply(
        lambda row: dt.calc_baseline(
            signal_df=row, x_col_key=x_col_key, y_col_key=y_col_key
        )
    )
    baseline_subtracted_signals = {}

    print("subtracting baselines..")
    for i in baselines.index:
        original_signal_df = df_series.loc[i]
        original_signal_time_axis = original_signal_df.iloc[:, 0]

        baseline_df = baselines[i]

        baseline_subtracted_y_axis = (
            original_signal_df.iloc[:, 1] - baseline_df.iloc[:, 1]
        )
        baseline_subtracted_y_axis_colname = (
            f"{list(original_signal_df.columns)[1]}_baseline_subtracted"
        )

        baseline_subtracted_signals[i] = pd.DataFrame()
        baseline_subtracted_signals[i][
            original_signal_time_axis.name
        ] = original_signal_time_axis
        baseline_subtracted_signals[i][
            baseline_subtracted_y_axis_colname
        ] = baseline_subtracted_y_axis

    baseline_subtracted_signals_series = pd.Series(baseline_subtracted_signals)
    baseline_subtracted_signals_series.name = "baseline_subtracted"

    return baseline_subtracted_signals_series


def interpolate_chromatogram_times(df_series: pd.Series):
    """
    Change the core function to act on a single dataframe, then wrap in a loop.
    """
    df_series.apply(lambda row: print(row.shape))
    # get range of time values
    max_time = 0
    min_time = 0

    max_time = max([row[list(row.columns)[0]].max() for row in df_series])
    min_time = min([row[list(row.columns)[0]].min() for row in df_series])

    print("interpolating common time axis across all input chromatograms:\n")
    print(f"min time point: {min_time}\n")
    print(f"max time point: {max_time}\n")

    time_points = np.linspace(
        start=min_time,
        stop=max_time,
        num=df_series.iloc[0][list(df_series.iloc[0].columns)[0]].shape[0],
    )

    print("interpolated time series:\n")
    print(
        f"range: {min(time_points)} to {max(time_points)} with length"
        f" {len(time_points)}"
    )

    # Interpolate all chromatograms to the common set of time points
    interpolated_chromatograms_series = pd.Series()

    for row_name, row in df_series.items():
        interpolated_chromatogram_df = (
            row.set_index(list(row)[0])
            .reindex(time_points, method="nearest")
            .interpolate()
            .reset_index()
        )
        interpolated_chromatograms_series[row_name] = interpolated_chromatogram_df

    interpolated_chromatograms_series.name = "time_interpolated"

    return interpolated_chromatograms_series


def peak_alignment(chromatogram_df_series: pd.Series, highest_corr_key: str):
    print("aligning chromatograms..")
    # Ensure that the data is the correct dtype
    chromatogram_df_series = chromatogram_df_series.apply(lambda row: row.astype(float))

    # Define reference chromatogram, convert to numpy array
    reference_chromatogram_np_array = (
        chromatogram_df_series[highest_corr_key].iloc[1].to_numpy()
    )

    # Create new series to store aligned chromatograms
    aligned_chromatograms_series = pd.Series()

    for key, chromatogram_df in chromatogram_df_series.items():
        query_chromatogram_np_array = chromatogram_df.iloc[1].to_numpy()

        # Calculate the DTW distance and path between the reference and current chromatogram
        alignment = dtw(
            query_chromatogram_np_array,
            reference_chromatogram_np_array,
            # open_end=True,
            # open_begin=True,
        )

        # Align the current chromatogram to the reference chromatogram using the calculated path
        aligned_chromatogram_np_array = np.zeros_like(reference_chromatogram_np_array)

        for i, cur_idx in enumerate(alignment.index2):
            ref_idx = alignment.index1[i]
            aligned_chromatogram_np_array[cur_idx] = query_chromatogram_np_array[
                ref_idx
            ]

        # Interpolate missing values in the aligned chromatogram
        valid_indices = np.where(aligned_chromatogram_np_array != 0)[0]
        if len(valid_indices) > 0:
            interp_func = np.interp(
                np.arange(len(aligned_chromatogram_np_array)),
                valid_indices,
                aligned_chromatogram_np_array[valid_indices],
            )
        else:
            interp_func = aligned_chromatogram_np_array

        # Replace the original chromatogram with the aligned and interpolated chromatogram
        aligned_chromatogram_df = chromatogram_df.copy()
        aligned_chromatogram_df.iloc[1] = interp_func
        aligned_chromatograms_series[key] = aligned_chromatogram_df

    aligned_chromatograms_series.name = "dtw_aligned"

    return aligned_chromatograms_series


# Assuming 'series_of_dataframes' is your input Series containing DataFrames of spectrum-chromatograms


def calculate_distance_matrix(series_of_dataframes: pd.Series):
    n_samples = len(series_of_dataframes)
    sample_names = series_of_dataframes.index

    # Initialize an empty distance matrix
    distance_matrix = np.zeros((n_samples, n_samples))

    # Iterate over unique combinations of sample pairs
    for sample_1, sample_2 in combinations(sample_names, 2):
        # Extract the DataFrames for each pair of samples
        df_1 = series_of_dataframes[sample_1]
        df_2 = series_of_dataframes[sample_2]

        # Convert DataFrames to numeric
        df_1 = df_1.apply(pd.to_numeric)
        df_2 = df_2.apply(pd.to_numeric)

        # Flatten the DataFrames and calculate the Euclidean distance
        flattened_df_1 = df_1.to_numpy().flatten()
        flattened_df_2 = df_2.to_numpy().flatten()
        distance = euclidean(flattened_df_1, flattened_df_2)

        # Fill the distance matrix symmetrically
        i, j = sample_names.get_loc(sample_1), sample_names.get_loc(sample_2)
        distance_matrix[i, j] = distance
        distance_matrix[j, i] = distance

    # Convert the distance matrix to a pandas DataFrame with appropriate row and column names
    distance_matrix_df = pd.DataFrame(
        distance_matrix, index=sample_names, columns=sample_names
    )

    return distance_matrix_df
