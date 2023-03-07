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

from scripts.core_scripts.data_interface import retrieve_uv_data

class Sequence:
    """
    Currently just going to contain the data files.
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
    def __init__(self, uv_file_path = str):
        self.path = uv_file_path
        self.data = None
        
    def extract_uv_data(self):

        for x in self.path.iterdir():
            if ".UV" in x.name:

                uv_data = retrieve_uv_data(rb.read(str(self.path)))

                return uv_data
            
            else:
                print("Could not find a .UV file.")


class Data_Obj:
    """
    A class representing the actual data of a signal. It will be initialised by 'extract_ch_data()' and contain signal metadata, a df of the data with time in mins and signal in mAU, and plotting functions, specifically peak and baseline detection.
    """
    def __init__(self, rb_obj_file, file_path):
        self.rb_obj_file = rb_obj_file
        self.path = file_path
        self.wavelength = self.rb_obj_file.metadata['signal'].split('=')[1][:5]
        
        x_axis = self.rb_obj_file.xlabels.reshape(-1,1) # time in mins for this data
        y_axis = self.rb_obj_file.extract_traces().transpose()
        self.data_df = pd.DataFrame(np.concatenate((x_axis, y_axis), axis = 1), columns = ['mins', 'mAU'])
    
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
        #self.data_files_dict = self.data_files_lister()

    def data_files_dicter(self):

        ch_list = []
        uv_list = []

        for x in self.path.iterdir():
            if x.name.endswith(".ch"):
                ch_list.append(x.name)
            if x.name.endswith(".UV"):

                uv_list.append(x.name)

        return {"ch_files" : ch_list, "uv_files" : uv_list}
    
    # def detector_name_to_nm(self):

    #     acq_macaml = self.path / r"acq.macaml"

    #     with open(acq_macaml, 'r', encoding = 'UTF-8') as f:

    #         xml_data = f.read()
            
    #         bsoup_xml = BeautifulSoup(xml_data, 'xml')
            
    #         content = bsoup_xml.Content.Section.children

    #         print(content)
    #         # return the Signal section of the acq.macaml file.

    #         # spectrum is contained in <Name>Spectrum</Name>

    #         # wavelength signals are contained in <Section><Name>Signals\Name><ID>Signals</ID>

    #         return content
        
    def extract_ch_data(self):
        """
        A function to extraact the ch data from the directory. It was necessary to implement this as a function to provide a 'switch' to parse the data, as that is a slow process.

        Calling this function returns a dict whose keys are the signal wavelengths, and value is a subdict containing the specific signal's information and the data itself.

        I will now be turning the subdict into its own Object so that I can add plotting functionality to it, specifically peak detection and baselines.
        """

        rb_obj = rb.read(str(self.path))

        ch_data_dict = {}

        for file in self.path.iterdir():

            if ".ch" in file.name:

                ch_data = Data_Obj(rb_obj.get_file(str(file.name)), file)
                
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
    
    def rb_object(self):
        """
        loads the whole target data dir, currently it just returns the method and the data.
        """
        rainbow_obj = rb.read(str(self.path))
        
        return rainbow_obj
    
    def get_uv_data(self):
        return UV_Data(self.path)
    
    def __str__(self):
        return f"{type(self)}\nname: {self.name}\nacq_date: {self.acq_date}\nacq_method path: {self.acq_method}\nsequence name: {self.sequence_name}\navailable data: {self.data_files_dict}"

# most of the classes were prototypes in 2023-03-02_adding-sequences-to-data-table.ipynb.

# Agilette will be the entry point to all other functionality, analogous to loading the chemstation program.

class Agilette:
    def __init__(self, path = str):
        self.path = Path(path)
        self.library = Library(self.path)
        
    def data_table(self):
                # need to form dicts for each column then combine them together into the DF. Its just gna display the objects of each data object. Q is though, from what list? self.data_file_dir Also I need to find a way to get the acq date without using rainbow.
        
        
        ids = [idx for idx, x in enumerate(self.library.all_data_files)]
        
        data_dict = {}
                   
        df = pd.DataFrame({
                           "names" : [x.name for x in self.library.all_data_files],
                           "path" : [x.path for x in self.library.all_data_files],
                           "sequence" : [x.sequence_name for x in self.library.all_data_files],
                           "desc" : [x.description for x in self.library.all_data_files]}, 
                           index = {"acq_dates" : [x.acq_date for x in self.library.all_data_files]}["acq_dates"])
        
        return df.sort_index(ascending = False)
            
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
    
def main():
    ag = Agilette("/Users/jonathan/0_jono_data/")

    
if __name__ == "__main__":
    
    main()