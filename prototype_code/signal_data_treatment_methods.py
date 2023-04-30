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