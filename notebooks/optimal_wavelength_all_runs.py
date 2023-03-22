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

def uv_data_addition(runs, lib):

    all_data = lib.all_data()

    def uv_data_extractor(run_name):
        # accesses the data dir through the all_data dict using the run name specified by filtering the data table.

        data_dir = all_data[run_name]

        uv_data = data_dir.load_spectrum().uv_data
        
        # uv_data is a df containing a spectrum with 'mins' as the first column

        return uv_data
    
    # # this line returns a series of dataframes 'uv_data'.

    uv_data_series = runs['run_name'].apply(uv_data_extractor)

    uv_data_series.index = runs['run_name'].values
    uv_data_series.name = 'uv_data'

    return uv_data_series

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
    """


    def baseline_calculator(nm_series):
        if isinstance(nm_series, pd.Series):
            baseline_fitter = Baseline(nm_series.index)
            baseline_y = baseline_fitter.iasls(nm_series.values)[0]

            return(baseline_y)
        
        else:
            print(f"nm_series is {type(nm_series)}, not a Series")

    # def column_accessor(spectrum):
    #     # access each nm column in spectrum df and apply baseline_calculator
    #     if isinstance(spectrum, pd.Series):
    #         return spectrum.apply(baseline_calculator)
    #     else:
    #         print(f"spectrum obj is {type(spectrum)}, not a DataFrame")

    def uv_data_accessor(spectrum_column):
        # access each row in the spectrum column and apply column accessor, then handle the return
        if isinstance(spectrum_column, pd.Series):
            scaled_baseline_dfs_series = spectrum_column.apply(baseline_calculator)
            scaled_baseline_dfs_series.name = 'scaled_baseline_dfs'

        else:
            print(f"spectrum_column is {type(spectrum_column)}, not a Series")


    spectrum_column.apply(uv_data_accessor)
    
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



def main():
    

    selected_runs = ['2023-03-07_DEBERTOLI_CS_001.D', '2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D', '2023-02-23_LOR-RISTRETTO.D']

    lib = Library(Path('/Users/jonathan/0_jono_data'), runs_to_load = selected_runs)

    print(lib.data_table())

    # runs = find_target_runs(lib)
    
    uv_data_series = uv_data_addition(runs, lib)

    # # merge the uv_data with the rest of the runs table from the right.
    # runs = pd.merge(runs, uv_data_series.to_frame(), left_on = 'run_name', right_index = True)

    # # set uv_data index to mins for scaling operation to follow
    # runs['uv_data'] = runs['uv_data'].apply(lambda x : x.set_index('mins'))

    # # scale the uv_data nm column-wise.
    
    # scaled_uv_data = uv_data_scaler(runs.set_index('run_name').loc[:,'uv_data'])

    # runs = pd.merge(runs, scaled_uv_data.to_frame(), left_on = 'run_name', right_index = True)
 
    # #its important to track what the index is of passed dataframes and Series in and out of .apply in order to get expected behavior. Set index to desired column often.

    # # Current modus operandi for transforming columns and adding them to the runs df:
    # # 1. define a transformation function wrapper in order to keep the code clean.
    # # 2. pass in the to-be-transformed column with index set to 'run_name' in order to be able to track what is what. Doesnt necessarily need to be run-names, its just that its easier to understand what is happening than the generic integer index.
    # # 3. Using .apply() on a Series will return a series, be prepared to handle that. Pass that series back out into the main() where you will perform a merge into the runs df.

    # # Baseline Calculator

    # #spectrum_baseline_calculation(runs.set_index('run_name').loc[:,'scaled_uv_data'])

    # #uv_data_baselines = 
    # #runs = pd.Merge(runs, , on_left = 'run_name', on_right = )


main()