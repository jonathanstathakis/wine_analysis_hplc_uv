"""
2023-05-06 00:29:02 A short program to observe the variation in chromatogram-spectrum matrix sizes which is causing errors in [signal_alignment_methods.calculate_distance_matrix](../../../users/jonathan/wine_analysis_hplc_uv/prototype_code/signal_alignment_methods.py) when certain pairs of samples have matrices of different sizes.
"""
import peak_alignment_spectrum_chromatograms
import pandas as pd
import itertools
from scipy.stats import mode

def observe_sample_matrix_shape_mismatch():
    df = get_all_sample_matrices()
    df = df.set_index('wine')
    
    matrix_shape_df = matrix_shapes(df['spectra'])

    row_mode = calc_dim_length_mode(matrix_shape_df['num_row'])
    col_mode = calc_dim_length_mode(matrix_shape_df['num_col'])

    df['reshaped_spectra'] = df.apply(lambda row : reshape_dataframe(row['spectra'], row_mode, col_mode), axis = 1)
    
    new_matrix_shape_df_series = matrix_shapes(df['reshaped_spectra'])

    print(new_matrix_shape_df_series)


def reshape_dataframe(df : pd.DataFrame, desired_rows : int = None, desired_columns : int = None) -> pd.DataFrame:
    """
    Reshape a dataframe to fit a desired shape. Takes a dataframe and optional number of desired rows or columns and reshapes the dataframe, either padding or subsetting, to match the desired shape. Returns a pandas DataFrame.
    """
    print(desired_rows, desired_columns)
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

def matrix_shapes(series : pd.Series) -> pd.DataFrame:
    """
    Take a series of dataframes and return a series of .shape with the same index.
    """

    shape_df = series.apply(lambda row: row.shape).rename('matrix_shape').to_frame()
    shape_df[['num_row','num_col']] = shape_df['matrix_shape'].apply(pd.Series)
    
    return shape_df

def get_all_sample_matrices():
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
    observe_sample_matrix_shape_mismatch()
    return None

if __name__ == "__main__":
    main()