import sys

import os

import pandas as pd

import numpy as np

from scipy.signal import find_peaks

pd.options.plotting.backend = 'plotly'

import plotly.graph_objs as go

from plotly.subplots import make_subplots

from sklearn.preprocessing import MinMaxScaler

from pybaselines import Baseline

# adds root dir 'wine_analyis_hplc_uv' to path.)
from agilette.agilette_core import Library

from pathlib import Path

from time import perf_counter

def uv_data_scaler(uv_data_column):

    """
    take the uv data, apply MinMaxScaler to each column of each spectrum, return the spectrums as a Series with the same index as runs so I can join in main()
    """

    scaler = MinMaxScaler()

    def scale_spectrum(spectrum):
        # scale each spectrum. MinMaxScaler.fit_transform() can handle dataframe inputs and natively scales column by column.
        try:
            scaled_spectrum = pd.DataFrame(scaler.fit_transform(spectrum), columns=spectrum.columns)
        except Exception as e:
            print(e)

        return scaled_spectrum
        
    # dataframe uv spectra with index as mins

    scaled_uv_data_series = uv_data_column.apply(lambda row : scale_spectrum(row))
    scaled_uv_data_series.name = 'scaled_uv_data'

    return scaled_uv_data_series

def spectrum_baseline_calculation(spectrum_column):
    """
    1. Instantiate the Baseline object by passing it the mins Series, i.e. the Column index.
    2. get the y values by passing each columns values to the Baseline object.

    input is runs.set_index('run_name').loc[:,'scaled_uv_data'], a Series of dataframes.
    """

    def baseline_calculator(nm_series_column):
        if isinstance(nm_series_column, pd.Series):
            baseline_fitter = Baseline(nm_series_column.index)
            baseline_y = baseline_fitter.iasls(nm_series_column.values)[0]

            return(baseline_y)
        
        else:
            print(f"nm_series is {type(nm_series_column)}, not a Series")

    return_spectrum_column = spectrum_column.apply(
                                                    lambda spectrum : spectrum.apply(baseline_calculator) 
                                                    if isinstance(spectrum, pd.DataFrame) else "error")

    if isinstance(return_spectrum_column, pd.Series):
        print('returning baselines')
        return_spectrum_column.name = 'scaled_uv_data_baselines'
        return return_spectrum_column
    else:
        print(f"return_spectrum_column is a {type(return_spectrum_column)}, not a Series" )
    

def main():
    
    time_1 = perf_counter()
    selected_runs = ['2023-03-07_DEBERTOLI_CS_001.D']#'2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D', '2023-02-23_LOR-RISTRETTO.D']

    lib = Library(Path('/Users/jonathan/0_jono_data'), runs_to_load = selected_runs)

    print(lib.data_table())

    runs = lib.data_table()
    
    runs['uv_data'] = runs['run_dir_obj'].apply(lambda run_dir : run_dir.load_spectrum().uv_data)

    # # set uv_data index to mins for scaling operation to follow
    runs['uv_data'] = runs['uv_data'].apply(lambda x : x.set_index('mins'))

    # # scale the uv_data nm column-wise.
    
    scaled_uv_data = uv_data_scaler(runs.set_index('run_name').loc[:,'uv_data'])

    runs = pd.merge(runs, scaled_uv_data.to_frame(), left_on = 'run_name', right_index = True)
    
    # #its important to track what the index is of passed dataframes and Series in and out of .apply in order to get expected behavior. Set index to desired column often.

    # # Current modus operandi for transforming columns and adding them to the runs df:
    # # 1. define a transformation function wrapper in order to keep the code clean.
    # # 2. pass in the to-be-transformed column with index set to 'run_name' in order to be able to track what is what. Doesnt necessarily need to be run-names, its just that its easier to understand what is happening than the generic integer index.
    # # 3. Using .apply() on a Series will return a series, be prepared to handle that. Pass that series back out into the main() where you will perform a merge into the runs df.

    # # Baseline Calculator
    baselines = spectrum_baseline_calculation(runs.set_index('run_name').loc[:,'scaled_uv_data'])
    
    runs = pd.merge(runs, baselines, left_on = 'run_name', right_index = True)

    print(runs['scaled_uv_data_baselines'].values)

    # Correct scaled UV data by subtracting the baseline


    time_2 = perf_counter()

    print(time_2-time_1)

main()

    
def find_target_runs(lib):
    lib_df = lib.data_table()

    # filter to 10cm avantor column runs with a uv spectrum file
    
    filter_2_1_methods = (lib_df['method'].str.contains("2_1*"))

    filter_uracil = (lib_df['sample_name'].str.contains("uracil*"))

    filter_has_uv = (lib_df['uv_files'].apply(len)==0)

    runs = lib_df.loc[(filter_2_1_methods & ~filter_uracil & ~filter_has_uv)]

    # below is a reduced runs set for prototyping, will need to be expanded to use the full set after the code is written.

    runs = runs.iloc[0:3]

    return runs