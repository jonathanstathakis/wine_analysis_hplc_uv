from pathlib import Path

from bs4 import BeautifulSoup

import rainbow as rb

import sys

import os

import numpy as np

import pandas as pd

from datetime import datetime

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

        ch_data_dict = {}

        for x in self.path.iterdir():

            if ".ch" in x.name:

                ch_data = rb.read(str(self.path)).get_file(x.name)

                ch_data_signal = ch_data.metadata['signal']

                data_df = pd.DataFrame(np.concatenate(
                                            (ch_data.xlabels.reshape(-1,1),
                                            ch_data.extract_traces().transpose()), axis = 1)
                                            , columns = ['mins', 'mAU'])
                
                ch_data_dict[ch_data_signal.split('=')[1][:5]] = {'signal_info' : ch_data_signal, 'data' : data_df}
                
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
        self.data_file_dir = Data_File_Dir(self.path)
        
    def data_table(self):
                # need to form dicts for each column then combine them together into the DF. Its just gna display the objects of each data object. Q is though, from what list? self.data_file_dir Also I need to find a way to get the acq date without using rainbow.
        
        
        ids = [idx for idx, x in enumerate(self.data_file_dir.all_data_files)]
        
        data_dict = {}
                   
        df = pd.DataFrame({
                           "names" : [x.name for x in self.data_file_dir.all_data_files],
                           "path" : [x.path for x in self.data_file_dir.all_data_files],
                           "sequence" : [x.sequence_name for x in self.data_file_dir.all_data_files],
                           "desc" : [x.description for x in self.data_file_dir.all_data_files]}, 
                           index = {"acq_dates" : [x.acq_date for x in self.data_file_dir.all_data_files]}["acq_dates"])
        
        return df.sort_index(ascending = False)
            
# An object to imitate the data directory that stores single run and sequence files.

#dict_3={k:v for d in (dict_1,dict_2) for k,v in d.items()}

class Data_File_Dir:

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

"""
a prototyped class definition using bits of rainbow and bits of direct XML parsing.

I'll keep building it from here as my use case increases, but it is barebones atm.

"""
    
def main():
    ag = Agilette("/Users/jonathan/0_jono_data/")

    
if __name__ == "__main__":
    
    main()