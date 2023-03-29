"""
a prototyped class definition using bits of rainbow and bits of direct XML parsing.

I'll keep building it from here as my use case increases, but it is barebones atm.

Current Heriarchy ( 2023-03-08 ):
- To access a single run's single signal data: 
    Agilette(dirpath).library.single_runs["run_name"].extract_ch_data()["wavelength_nm"]["data"]
- To access a sequence run's signal signal data:
    Agilette(dirpath).library.sequences["sequence_name"].data_files["run_name"].extract_ch_data()["wavelength_nm"]["data"]
- To access a sequence run's UV data:
    Agilette.library.sequences["sequence_name"].data_files["run_name"].extract_Spectrum()

TODO: Add a plotting function to the Data class
TODO: add functionality to the Library Object, i.e. a help string and print behavior, such as a list of all the contained runs and sequences.
TODO: add proper type hints to EVERYTHING. Identify whether path can be PosixPath in every case, otherwise make it so.
"""

from pathlib import Path
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objs as go

#from agilette.run_dir import Run_Dir

from scripts.core_scripts.data_interface import retrieve_uv_data

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
    
class Spectrum:
    """
    A class representing the UV data of a run. It will be initialised by 'extract_Spectrum()' and contain the UV data as a Spectrum object.
    """
    def __init__(self, path : Path):
        self.path = path
        
    def extract_spectrum(self):
            self.spectrum = retrieve_uv_data(self.path)
            #return self.spectrum
            return self
    
    def line_plot(self):
        """
        it appears that there is a bug around here causing certain columns not to plot, the current example being nm's from 216 - 220nm missing from a 3d line plot. No obvious reason why.
        """
        from scripts.core_scripts.hplc_dad_plots import plot_3d_line

        plot_3d_line(self.spectrum, self.path.name)

class Single_Signal:
    """
    A class representing the actual data of a signal. It will be initialised by 'extract_ch_data()' and contain signal metadata, a df of the data with time in mins and signal in mAU, and plotting functions, specifically peak and baseline detection.
    """
    def __init__(self, rb_obj_file, file_path):
        self.rb_obj_file = rb_obj_file
        self.path = file_path
        self.wavelength = rb_obj_file.ylabels[0]
        self.x_axis = self.rb_obj_file.xlabels.reshape(-1,1) # time in mins for this data
        self.y_axis = self.rb_obj_file.extract_traces().transpose()
        self.data_df = pd.DataFrame(np.concatenate((self.x_axis, self.y_axis), axis = 1), columns = ['mins', 'mAU'])

    
    def plot(self, baseline = False, peak_detect = False):

        # base level plot

        fig = go.Figure()
        
        base_plot = go.Scatter(x = self.data_df['mins'], y = self.data_df['mAU'], mode = 'lines', name = f"{self.path.name} {self.wavelength}nm")

        fig.add_trace(base_plot)

        fig.update_layout(
                        title = f"{self.path.name} {self.wavelength}nm",
                        xaxis_title = "Time (mins)",
                        yaxis_title = "Signal (mAU)")

        fig.show()



class Agilette:
    def __init__(self, path: str):
        self.path = Path(path)
        #self.library = library(self.path)


            
# An object to imitate the data directory that stores single run and sequence files.

#dict_3={k:v for d in (dict_1,dict_2) for k,v in d.items()}
    
def main():
    ag = Agilette("/Users/jonathan/0_jono_data/")

    
if __name__ == "__main__":
    
    main()