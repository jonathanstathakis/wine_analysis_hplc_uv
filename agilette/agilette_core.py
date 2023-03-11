"""
a prototyped class definition using bits of rainbow and bits of direct XML parsing.

I'll keep building it from here as my use case increases, but it is barebones atm.

Current Heriarchy ( 2023-03-08 ):
- To access a single run's single signal data: 
    Agilette(dirpath).library.single_runs["run_name"].extract_ch_data()["wavelength_nm"]["data"]
- To access a sequence run's signal signal data:
    Agilette(dirpath).library.sequences["sequence_name"].data_files["run_name"].extract_ch_data()["wavelength_nm"]["data"]
- To access a sequence run's UV data:
    Agilette.library.sequences["sequence_name"].data_files["run_name"].extract_uv_data()

TODO: Add a plotting function to the Data class
TODO: add functionality to the Library Object, i.e. a help string and print behavior, such as a list of all the contained runs and sequences.
"""

from pathlib import Path

from bs4 import BeautifulSoup

import rainbow as rb

import sys

import os

import numpy as np

import pandas as pd

from datetime import datetime

import plotly.graph_objs as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from scripts.acaml_read import signal_metadata

from scripts.core_scripts.data_interface import retrieve_uv_data

class Sequence:
    """
    Currently just going to contain the data files.

    todo: add start dates.
    """
    def __init__(self, file_path):
        self.path = file_path
        self.data_files = self.data_files()

    def data_files(self):
        
        try:
            data_file_dict = {Run_Dir(x).name : Run_Dir(x) for x in self.path.iterdir() if x.name.endswith(".D")}
                    
        except Exception as e:
            print(f"{e}")
        
        return data_file_dict
        
    def __str__(self):
        return f"{self.path.name}, {self.data_files.keys()}"
    
class UV_Data:
    """
    A class representing the UV data of a run. It will be initialised by 'extract_uv_data()' and contain the UV data as a Spectrum object.
    """
    def __init__(self, uv_file_path = str):
        self.path = uv_file_path
        self.data = None
        self.uv_data = None
        
    def extract_uv_data(self):

        try:
            for x in self.path.iterdir():
                if ".UV" in x.name:

                    uv_data = retrieve_uv_data(rb.read(str(self.path)))

                    self.uv_data = uv_data

                    print("uv_data extracted")
        
        except Exception as e:
            print(e)
    
    def line_plot(self):
        """
        it appears that there is a bug around here causing certain columns not to plot, the current example being nm's from 216 - 220nm missing from a 3d line plot. No obvious reason why.
        """
        from scripts.core_scripts.hplc_dad_plots import plot_3d_line

        plot_3d_line(self.uv_data, self.path.parent.name)

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

class Run_Dir:
    """
    A single run directory containing signal data and metadata about the run.

    Use extract_uv_data(self) to get the Spectrum.

    To get ch data, it is useful to view each signal's wavelength and band rather than the detector name, so run self.extract_ch_data() to get a dictionary of each signal with its wavelength as the key and dataframe of the signal as value.
    """
    def __init__(self, file_path):
        self.path = file_path
        self.name, self.description, self.acq_method = self.load_meta_data()
        self.metadata = self.load_meta_data()
        self.acq_date = self.get_acq_datetime()
        self.sequence_name = self.sequence_name()
        self.data_files_dict = self.data_files_dicter()
        self.single_signals_metadata, self.spectrum_metadata = self.get_signal_metadata()

    def __str__(self):
        print_string =  f"{type(self)}\nname: {self.name}\nacq_date: {self.acq_date}\nacq_method path: {self.acq_method}\nsequence name: {self.sequence_name}\nAvailable Data:"
        
        for item in self.single_signals_metadata.items():
            print_string = print_string + str(item) + "\n"
        
        print_string = f"{print_string}\nSpectrum:\n"
        print_string = f"{print_string}\n{self.spectrum_metadata}"
        #available data: {self.data_files_dict}"

        return print_string

    def get_signal_metadata(self):
        return signal_metadata(self.path)

    def data_files_dicter(self):

        ch_list = []
        uv_list = []

        for x in self.path.iterdir():
            if x.name.endswith(".ch"):
                ch_list.append(x.name)
            if x.name.endswith(".UV"):

                uv_list.append(x.name)

        return {"ch_files" : ch_list, "uv_files" : uv_list}

    def extract_ch_data(self):
        """
        A function to extraact the ch data from the directory. It was necessary to implement this as a function to provide a 'switch' to parse the data, as that is a slow process.

        Calling this function returns a dict whose keys are the signal wavelengths, and value is a subdict containing the specific signal's information and the data itself.

        I will now be turning the subdict into its own Object so that I can add plotting functionality to it, specifically peak detection and baselines.
        """

        rb_obj = rb.read(str(self.path))

        ch_data_dict = {}

        for file in self.path.iterdir():
            """
            TODO: need to get the dict keys (or output) to be sorted by wavelength from lowest to highest.
            """

            if ".ch" in file.name:

                ch_data = Single_Signal(rb_obj.get_file(str(file.name)), file)
                
                ch_data_dict[ch_data.wavelength] = ch_data
                
        return ch_data_dict

    
    def sequence_name(self):
        
        # note: can only have UPPER CASE naming in Chemstation. Maybe should introduce a lower() function during data read. In fact, should probably include a data cleaning function of some kind. In the mean time, just add upper case to this if statement.
        
        if (".sequence" or ".SEQUENCE") in self.path.parent.name:
            return self.path.parent.name
        else:
            return "single run"
    
    def get_acq_datetime(self):
        with open(self.path / 'RUN.LOG', encoding = '<UTF-16LE>') as f:
            doc = f.read()
            
            idx = doc.index("Method started")
            acq_datetime = datetime.strptime(doc[idx+47:idx+64], "%H:%M:%S %m/%d/%y")
        
            return acq_datetime
                                                
    def load_meta_data(self):
        
        """
        atm this loads the name and description from SAMPLE.XML found in .D dirs.
        It also cleans the description string.
        
        Atm it needs to load the whole XML file to read these two tags, which seems inefficient
        but i dont know how to do it otherwise.
        """
        try:
            with open(self.path / r"SAMPLE.XML", 'r', encoding = 'UTF-16LE') as f:

                xml_data = f.read()
                
                bsoup_xml = BeautifulSoup(xml_data, 'xml')
                
                name = bsoup_xml.find("Name").get_text()
                
                description = bsoup_xml.find("Description").get_text()

                if not description:
                    description = "empty"
                
                else:
                    description = description.replace("\n", "").replace(" ", "-").strip()
                
                acq_method = bsoup_xml.find("ACQMethodPath").get_text()

            return name, description, acq_method
        
        except Exception as e:
            print(f"error loading metadata from {self.path}: {e}")
    
    def rb_object(self):
        """
        loads the whole target data dir, currently it just returns the method and the data.
        """
        rainbow_obj = rb.read(str(self.path))
        
        return rainbow_obj
    
    def get_uv_data(self):
        return UV_Data(self.path)

# most of the classes were prototypes in 2023-03-02_adding-sequences-to-data-table.ipynb.

# Agilette will be the entry point to all other functionality, analogous to loading the chemstation program.

class Agilette:
    def __init__(self, path = str):
        self.path = Path(path)
        self.library = Library(self.path)
            
# An object to imitate the data directory that stores single run and sequence files.

#dict_3={k:v for d in (dict_1,dict_2) for k,v in d.items()}

class Library:

    def __init__(self, dir_path):
    
        self.path = dir_path
        self.single_runs = self.single_runs()
        self.sequences = self.sequences()
        self.all_data_files = self.all_data_files()
    
    def single_runs(self):
        
        single_run_dict = {obj.name : Run_Dir(obj) for obj in self.path.iterdir() if obj.name.endswith(".D")}
        
        return single_run_dict
                        
    def sequences(self):
        
        sequence_dict = {sequence_dir.name : Sequence(sequence_dir) for sequence_dir in self.path.iterdir() if sequence_dir.name.endswith(".sequence")}
        
        return sequence_dict
    
    def combined_dict(self):
            
        import re
        
        # combine all D dirs together into a dict. To handle duplicate file names across sequences and single runs, we will add a counter to the key name.
        
        all_data = {}

        dup_suffix = 1

        loop_count = 0

        for x in self.path.glob('**/*.D'):
            
            loop_count += 1
            if x.name not in all_data.keys():

                print(f"{x.name} is not in all_data.keys()")

                print(f"{x.name} added for the first time")

                all_data[x.name] = Run_Dir(x)
                continue
                
            if x.name in all_data.keys():
                print(f"{x.name} is in all_data.keys()")
                new_name = f"{x.name}_{dup_suffix}"
                dup_suffix += 1

                print(f"renaming {x.name} as {new_name} to avoid duplicates in dict")
    
                all_data[new_name] = Run_Dir(x)

            
            
            # else:
            #     if x.name in all_data.keys() and x.is_dir():
            #         print(x)
            #         print(f"duplicate found {x.name}")

            #         suffix += 1
            #         print(f"dup count: {dup_count}")

            #         dup_key_name = f"{x.name}_{dup_count}"

            #         print(f"duplicate name {dup_key_name}")

            #         all_data[f"{x.name}_{dup_count}"] = Run_Dir(x)

            # print("leaving iteration")

        #combined_dict = {**self.single_runs, **self.sequences.values().data_files}
            
        return all_data

    def all_data_files(self):
        
        # sequences
        seq_list = []
        
        for data_dir in self.sequences.values():
            for y in data_dir.data_files.values():
                seq_list.append(y)
        # single runs
        run_list = []
        
        for x in self.single_runs.values():
            run_list.append(x)
            
        all_data_list = seq_list + run_list
        
        return(all_data_list)
    
    def data_table(self):
                # need to form dicts for each column then combine them together into the DF. Its just gna display the objects of each data object. Q is though, from what list? self.data_file_dir Also I need to find a way to get the acq date without using rainbow.
        
        
        ids = [idx for idx, x in enumerate(self.all_data_files)]

        data_dict = {}
                   
        df = pd.DataFrame({
                           "acq_date" : [x.acq_date for x in self.all_data_files],
                           "name" : [x.name for x in self.all_data_files],
                           "path" : [x.path for x in self.all_data_files],
                           "sequence" : [x.sequence_name for x in self.all_data_files],
                           "ch_files" : [x.data_files_dict['ch_files'] for x in self.all_data_files],
                           "uv_files" : [x.data_files_dict['uv_files'] for x in self.all_data_files],
                           "method" : [x.acq_method for x in self.all_data_files],
                           "desc" : [x.description for x in self.all_data_files]
                           })
        
        return df.sort_values('acq_date', ascending = False)
    
def main():
    ag = Agilette("/Users/jonathan/0_jono_data/")

    
if __name__ == "__main__":
    
    main()