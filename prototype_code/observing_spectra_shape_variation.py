"""
2023-05-06 00:29:02 A short program to observe the variation in chromatogram-spectrum matrix sizes which is causing errors in [signal_alignment_methods.calculate_distance_matrix](../../../users/jonathan/wine_analysis_hplc_uv/prototype_code/signal_alignment_methods.py) when certain pairs of samples have matrices of different sizes.
"""
import peak_alignment_spectrum_chromatograms
import pandas as pd
import itertools
from scipy.stats import mode
import numpy as np

def observe_sample_size_mismatch():
    """
    2023-05-06 13:23:35 
    
    1. form a dataframe `df` of samples with wine, new_id, spectra.
    2. set the index of the dataframe to 'wine' to preserve those names during Series.apply operations on the spectra column.
    3. Construct `size_df`, a dataframe of 'ms', 'ns' for each sample row, with index = 'wine'
    4. calculate the 'm' and 'n' mode for the library from `size_df`.
    5. display sample name and spectra shapes of thoes which deviate from the library mode.
    6. Reshape deviated spectra to match the library mode IF distance from the mode is not >10%, if is, notify user.
    """

    # form dataframe of samples with columns 'wine', 'new_id', 'spectra', set index to 'wine' to preserve during columnar operations.
    df = get_all_sample_matrices()
    print(df.columns)
    df = df.set_index('wine')
    
    # # form dataframe of wine : 'size' | 'm' | 'n'
    # shape_df = get_matrix_shapes(df['spectra'])
    
    # place a function to describe deviations in the library from the shape means.
    
    raw_matrix_report = report_deviating_shapes(df['spectra'])
    #print(raw_matrix_report)

    # Adjust pandas display options

    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    matrix_report = raw_matrix_report.join(df.drop(['spectra'], axis =1))
    # print(matrix_report.drop('path', axis = 1))
    # print(matrix_report['path'])

    # extract the modes of each dimension as numeric.
    m_mode = matrix_report['m_mode'].max()
    n_mode = matrix_report['n_mode'].max()

    # reshape the input matrixes to match the mode, either padding or slicing
    df['reshaped_matrix'] = df.apply(lambda row : reshape_dataframe(row['spectra'], m_mode, n_mode), axis = 1)
    new_size_df_series = get_matrix_shapes(df['reshaped_matrix'])

    # print deviating shapes report after resizing
    new_size_df_series_raw_report = report_deviating_shapes(df['reshaped_matrix'])
    print(new_size_df_series_raw_report)

    

def report_deviating_shapes(matrix_series : pd.Series):
    """
    Takes a series containing dataframes, finds deviations from the mode of each dimension, returns a DataFrame report.
    
    1. find the shapes of the dataframes.
    2. for each dimension, find the mode.
    3. for each dimension, calculate magnitude of deviations from the mode.
    4. for each dimension, return a report df.
    5. concat the report df's together.
    6. in report df, filter out rows for which deviation in both dimensions == 0.
    7. return filtered report df.
    """
    
    def dim_size_deviation_report(size_series : pd.Series):
        try:

            # Find the mode of the shapes
            dim_mode = mode(size_series, keepdims = True)[0][0]

            # Calculate the deviation for each DataFrame's shape from the mode
            deviations = size_series.apply(lambda shape: np.abs(np.subtract(shape, dim_mode)).sum())

            ##deviations = deviations.

            report = pd.DataFrame({
                f'{size_series.name}_mode': dim_mode,
                f'{size_series.name}_shape': size_series,
                f'{size_series.name}_deviation': deviations,
                f'{size_series.name}_%_deviation': round(deviations/dim_mode * 100,2)})

        except Exception as e:
            print(e)
            print(size_series)
            report = None

        return report
    
    shape_df = get_matrix_shapes(matrix_series)

    m_report = dim_size_deviation_report(shape_df['m'])
    n_report = dim_size_deviation_report(shape_df['n'])

    join_report = m_report.join(n_report)

    filtered_join_report = join_report.query("m_deviation != 0 or n_deviation !=0")
    
    return filtered_join_report
    
def reshape_dataframe(df : pd.DataFrame, desired_rows : int = None, desired_columns : int = None) -> pd.DataFrame:
    """
    Reshape a dataframe to fit a desired shape. Takes a dataframe and optional number of desired rows or columns and reshapes the dataframe, either padding or subsetting, to match the desired shape. Returns a pandas DataFrame.
    """
    # If desired_rows or desired_columns is not provided, use the current DataFrame shape
    if desired_rows is None:
        desired_rows = df.shape[0]
    if desired_columns is None:
        desired_columns = df.shape[1]

    # Subset or pad rows
    if desired_rows < df.shape[0]:
        df = df.iloc[:desired_rows]
    else:
        new_index = range(desired_rows)
        df = df.reindex(index=new_index, fill_value=0)

    # Subset or pad columns
    if desired_columns < df.shape[1]:
        df = df.iloc[:, :desired_columns]
    else:
        new_columns = range(desired_columns)
        df = df.reindex(columns=new_columns, fill_value=0)

    return df

def get_matrix_shapes(series : pd.Series) -> pd.DataFrame:
    """
    Take a series of dataframes and return a series of .shape with the same index.
    """

    shape_df = series.apply(lambda row: row.shape).rename('size').to_frame()
    shape_df[['m','n']] = shape_df['size'].apply(pd.Series)
    
    return shape_df

def get_all_sample_matrices():
    """
    2023-05-06 14:35:05 returns a df of Index(['new_id', 'wine', 'spectra'], dtype='object')
    """
    df = peak_alignment_spectrum_chromatograms.load_spectrum_chromatograms()
    return df

def form_unique_sample_pairs(df : pd.DataFrame) -> list:
    """
    Form a sequence of unique pairs, where pairs respect the cummutative property AB = BA.
    
    number of unique pairs = n(n-1)/2 = 60*59/2 = 1770 pairs.
    """
    # Generate all unique pairs of rows
    row_pairs = list(itertools.combinations(df.iterrows(), 2))
    print(len(row_pairs))

    # # Process and print the pairs
    # for pair in row_pairs:
    #     row_1 = pair[0][1]
    #     row_2 = pair[1][1]
    #     print(row_1['wine'], row_2['wine'])

    return row_pairs

def calc_dim_length_mode(series : pd.Series):
    
    dim_mode = mode(series, keepdims = True)[0][0]

    return dim_mode

def main():
    observe_sample_size_mismatch()
    return None

if __name__ == "__main__":
    main()