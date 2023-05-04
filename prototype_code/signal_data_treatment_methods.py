"""
A file to contain all the general data treatment methods: baseline correction, mean centering, normalization, peak alignment, peak finding, etc.
"""
import pandas as pd
from pybaselines import Baseline
import numpy as np
from scipy.signal import  find_peaks
import streamlit as st

def calc_baseline(signal_df : pd.DataFrame, x_col_key : str, y_col_key : str) -> pd.DataFrame:
    """
    Create baseline obj then fit the baseline on it. return baseline as df of ['mins','mAU']
    """
    baseline_obj = Baseline(signal_df[x_col_key])
    baseline_y = baseline_obj.iasls(signal_df[y_col_key])[0]
    baseline_df = signal_df[[x_col_key]].copy(deep = True)
    baseline_df[y_col_key] = baseline_y
    return baseline_df

def baseline_area(df : pd.DataFrame) -> float:
    """
    calculate area under the baseline curve
    """
    area = np.trapz(y = df['mAU'], x = df['mins'])
    return area

def peak_finder(signal_df : pd.DataFrame, in_height = None, in_prominence = None) -> pd.DataFrame:
    """
    find peaks for a given signal df, returned as a df of ['mins', 'mAU']
    """
    peak_idx, peak_y = find_peaks(signal_df['254'], height = in_height, prominence = in_prominence)
    peak_y = peak_y['peak_heights']
    peak_x = signal_df['mins'][peak_idx]
    peak_df = pd.DataFrame(zip(peak_x, peak_y), columns = ['mins', 'mAU'])
    print(peak_df.shape)
    return peak_df

def extract_single_wavelength(df_series : pd.DataFrame, wavelength : str) -> pd.DataFrame:
    """
    Given a dataframe containing
    """
    def get_wavelength(spectrum_df : pd.DataFrame, wavelength) -> pd.DataFrame:
        spectrum_df = spectrum_df.set_index('mins')
        single_wavelength_df = spectrum_df[wavelength]
        single_wavelength_df = single_wavelength_df.to_frame().reset_index()

        return single_wavelength_df
    
    single_wavelength_series = pd.Series(df_series.apply(lambda row : 
    get_wavelength(row, wavelength)),index = df_series.index)

    return single_wavelength_series

def subtract_baseline_from_spectra(df : pd.DataFrame)  -> pd.DataFrame:
    """
    Subtract baseline from each column of a spectrum  as a pandas dataframe of column format RangeIndex | mins | wavelength_1, .. , wavelength_n.

    Only pass in mins and the wavelength columns.
    """

    def check_non_numeric_columns(df):
        non_numeric_columns = ~df.dtypes.apply(pd.api.types.is_numeric_dtype)
        if non_numeric_columns.any():
            non_numeric_column_names = df.columns[non_numeric_columns].tolist()
            raise ValueError(f"\nError: dataframe with non-numeric columns passed to subtract_baseline_from_spectra(). Non-numeric columns: {non_numeric_column_names}\n")
    
    try:
        check_non_numeric_columns(df)
    except ValueError as e:
        print(e)
    
    baseline_obj = Baseline(df['mins'])
    names = df['name_ct']
    df = df.drop(['hash_key', 'name_ct'], axis = 1)
    baseline_df = df.apply(lambda spectrum_col : baseline_obj.iasls(spectrum_col)[0])
    baseline_subtracted_spectra_df = df - baseline_df
    baseline_subtracted_spectra_df['name_ct'] = names
    return baseline_subtracted_spectra_df

def test_baseline_correction():
    import duckdb as db
    con = db.connect('wine_auth_db.db')

    query_1 = """
    SELECT A.*,
        sub_query.name_ct
    FROM
        spectrums A
    JOIN (
        SELECT
            hash_key,
            name_ct
        FROM
            super_table
        LIMIT
        1    
    ) sub_query
    ON
        A.hash_key = sub_query.hash_key;
    """

    spectra_df = con.sql(query_1).df()

    baseline_subtracted_df = subtract_baseline_from_spectra(spectra_df)

    import matplotlib.pyplot as plt

    baseline_subtracted_df.plot(title = baseline_subtracted_df['name_ct'].values[0])
    #plt.show()


def main():
    test_baseline_correction()

if __name__ == "__main__":
    main()
