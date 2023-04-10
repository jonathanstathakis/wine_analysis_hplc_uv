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
        - [ ] calculate area under baseline.
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
from pybaselines import Baseline
from scipy.signal import  find_peaks
from agilette.modules.metadata_sampletracker_cellartracker_join import agilent_sample_tracker_cellartracker_super_table as super_table
from agilette.modules.library import Library
from agilette.modules.run_dir import Run_Dir
import matplotlib.pyplot as plt


import streamlit as st

def main():
    #df = super_table()
    lib = Library(Path('/Users/jonathan/0_jono_data/2023-02-22_STONEY-RISE-PN_02-21.D'))
    lib = lib.load_spectrum()

    # extract single wavelength from spectrum.
    def nm_extractor(spectrum : pd.DataFrame, nm : str) -> pd.DataFrame :
        """
        Take a spectrum df and extract one wavelength, returning as a df of ['mins', 'mAU'].
        """
        nm_df = spectrum.loc[:,['mins', nm]]
        return nm_df

    # apply nm_extractor to each row of lib['spectrum'], a series of df's.
    lib['nm_254'] = pd.Series(lib.apply(lambda row : nm_extractor(row['spectrum'],'254'), axis = 1))

    # fit the baseline to that wavelength.
    def signal_baseline_creator(signal_df : pd.DataFrame) -> pd.DataFrame:
        """
        Create baseline obj then fit the baseline on it. return baseline as df of ['mins','mAU']
        """
        baseline_obj = Baseline(signal_df['mins'])
        baseline_y = baseline_obj.iasls(signal_df['254'])[0]
        baseline_df = signal_df[['mins']].copy(deep = True)
        baseline_df['mAU'] = baseline_y
        return baseline_df
    
    # create a baseline column.
    lib['baseline_254'] = pd.Series(lib.apply(lambda row : signal_baseline_creator(row['nm_254']), axis = 1))

    # calculate area under the baseline curve

    def baseline_area(df : pd.DataFrame) -> float:

        area = np.trapz(y = df['mAU'], x = df['mins'])

        print(area)

    lib['baseline_254_area'] = pd.Series(lib.apply(lambda row :  baseline_area(row['baseline_254']), axis = 1))

main()



