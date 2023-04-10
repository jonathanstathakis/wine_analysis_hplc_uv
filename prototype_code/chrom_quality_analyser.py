"""
See 2023-04-10_logbook.md.

A master file to develop generalised transformation and statistical calculation of chromatogram signals in Agilette.
TODO:
    - [ ] get the selected avantor runs.
    - [ ] load and plot a spectrum.
    - [ ] for a Series of DataFrames:
        - [ ] select 255nm wavelength.
        - [ ] plot 255nm wavelength.
        - [ ] fit baseline.
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

def main():
    #df = super_table()
    lib = Library(Path('/Users/jonathan/0_jono_data/2023-02-22_STONEY-RISE-PN_02-21.D'))
    lib = lib.load_spectrum()

    def nm_extractor(spectrum : pd.DataFrame, nm : str) -> pd.DataFrame :
        """
        Take a spectrum df and extract one wavlength, returning as a df of ['mins', 'mAU'].
        """

        nm_df = spectrum.loc[:,['mins', nm]]

        return nm_df

    lib['nm_254 series'] = pd.Series(lib.apply(lambda x : nm_extractor(x['spectrum'],'254'), axis = 1))

    

main()



