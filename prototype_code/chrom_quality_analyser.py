"""
See 2023-04-10_logbook.md.

A master file to develop generalised transformation and statistical calculation of chromatogram signals in Agilette.
TODO:
    - [ ] get the selected avantor runs.
    - [x] load and plot a spectrum.
    - [ ] for a Series of DataFrames:
        - [x] select 254nm wavelength.
        - [x] plot 254m wavelength.
        - [x] fit baseline.
        - [x] calculate area under baseline.
        - [ ] display  distribution of area under baseline.
        - [ ] calculate peak prominance of 255nm spectrum.
        - [ ] display distribution of peak prominance.
        - [ ] Calculate ratio of the two.
        - [ ] display distribution of ratio.
"""
from pathlib import Path
import sys
sys.path.append('../')
import pandas as pd
import numpy as np
from agilette.modules.metadata_sampletracker_cellartracker_join import agilent_sample_tracker_cellartracker_super_table as super_table
from agilette.modules.library import Library
from agilette.modules.run_dir import Run_Dir
import plotly.graph_objects as go
import streamlit as st
import inspect
import signal_data_treatment_methods as dt

st.set_page_config(layout = 'wide')

# inspect.currentframe().f_code.co_name

def test_df_empty(df : pd.DataFrame, func_name : str) -> pd.DataFrame:
    if df.empty:
        raise ValueError(f'in {func_name}, passed df is empty')
    else:
        return df

# extract single wavelength from spectrum.
def nm_extractor(spectrum : pd.DataFrame, nm : str) -> pd.DataFrame:
    """
    Take a spectrum df and extract one wavelength, returning as a df of ['mins', 'mAU'].
    """
    nm_df = spectrum.loc[:,['mins', nm]]
    nm_df = test_df_empty(nm_df,inspect.currentframe().f_code.co_name)
    return nm_df

def update_peak_trace(lib, prominence_slider):
        
    new_peaks = lib.apply(lambda row : dt.peak_finder(row['nm_254'], 0.05, in_prominence = prominence_slider), axis = 1)
    new_x = new_peaks[0]['mins']
    new_y = new_peaks[0]['mAU']
    
    st.write(len(new_y))
    
    fig.update_traces(x = new_x, y = new_y, selector = dict(name = 'peaks trace'))

def streamlit_peak_finding(signal_df : pd.DataFrame, baseline_df : pd.DataFrame, peak_df : pd.DataFrame):

    trace_signal = go.Scatter(x = signal_df['mins'], y = signal_df['254'], mode = 'lines', name = 'signal trace')
    trace_baseline = go.Scatter(x = baseline_df[0]['mins'], y =  baseline_df[0]['mAU'], mode = 'lines', name = 'baseline trace')
    #trace_peaks = go.Scatter(x =peak_df['mins'], y = peak_df['mAU'], mode = 'markers', name = 'peaks trace')

    with st.container():
        prominence_slider = st.slider('select a value for peak prominence', min_value = 0, max_value = 100)
        fig = go.Figure()
        fig.update_layout(height = 800, width = 1200)
        fig.add_traces([trace_signal, trace_baseline
        #trace_peaks
        ])
        #update_peak_trace(lib, prominence_slider)
        st.plotly_chart(fig)

def main():
    #df = super_table()
    lib = Library(Path('/Users/jonathan/0_jono_data/2023-02-22_STONEY-RISE-PN_02-21.D'))
    lib = lib.load_spectrum()

    # apply nm_extractor to each row of lib['spectrum'], a series of df's.
    lib['nm_254'] = pd.Series(lib.apply(lambda row : nm_extractor(row['spectrum'],'254'), axis = 1))
    lib['nm_254']
    # create a baseline column.
    # fit the baseline to that wavelength.
    lib['baseline_254'] = pd.Series(lib.apply(lambda row : dt.calc_baseline(row['nm_254']), axis = 1))

    # create baseline AUC column
    lib['baseline_254_area'] = pd.Series(lib.apply(lambda row :  dt.baseline_area(row['baseline_254']), axis = 1))

    # calculate peak prominances
    # to do this will need to locate the peaks and provide them to peak_prominances as a 'sequence', i.e. list or series.
    # 1. Locate peaks
    # identify peaks using scipy.signal.find_peaks
    lib['peaks_254'] = lib.apply(lambda row : dt.peak_finder(row['nm_254'], 0.05, 2), axis = 1)

    streamlit_peak_finding(lib['nm_254'][0], lib['baseline_254'], lib['peaks_254'])
        
main()

