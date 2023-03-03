from pathlib import Path

from bs4 import BeautifulSoup

import rainbow as rb

import sys

import os

import numpy as np

import pandas as pd

from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from scripts.core_scripts.data_interface import retrieve_uv_data

class Sequence:
    
    """
    Currently just going to contain the data files.
    """
    def __init__(self, file_path):
        self.path = file_path
        self.data_dict = self.data_dict()

    def data_dict(self):
        
        try:
            data_file_dict = {Data(x).name : Data(x) for x in self.path.iterdir() if x.name.endswith(".D")}
                    
        except Exception as e:
            print(f"{e}")
        
        return data_file_dict
        
    def __str__(self):
        return self.path.name
    
class Data:
    
    def __init__(self, file_path):
        self.path = file_path
        self.name, self.description, self.acq_method = self.load_meta_data()
        self.metadata = self.load_meta_data()
        self.acq_date = self.get_acq_datetime()
        self.sequence_name = self.sequence_name()

    def extract_uv_data(self):

        for x in self.path.iterdir():
            if ".UV" in x.name:

                uv_data = retrieve_uv_data(rb.read(str(self.path)))

                return uv_data
    
    def extract_ch_data(self):

        ch_data_dict = {}

        for x in self.path.iterdir():

            if ".ch" in x.name:

                ch_data = rb.read(str(self.path)).get_file(x.name)
                
                ch_data_dict[x.name] = np.concatenate((ch_data.xlabels.reshape(-1,1),ch_data.extract_traces().transpose()), axis = 1)
        
        return ch_data_dict
    
    def sequence_name(self):
        if ".sequence" in self.path.parent.name:
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
    
    def __str__(self):
        return self.name

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
        self.sequence_dict = self.sequence_dict()
        self.all_data_files = self.all_data_files()
    
    def single_runs(self):
        
        single_run_dict = {obj.name : Data(obj) for obj in self.path.iterdir() if obj.name.endswith(".D")}
        
        return single_run_dict
                        
    def sequence_dict(self):
        
        sequence_dict = {obj.name : Sequence(obj) for obj in self.path.iterdir() if obj.name.endswith(".sequence")}
        
        return sequence_dict
    
    def all_data_files(self):
        
        # sequences
        seq_list = []
        
        for x in self.sequence_dict.values():
            for y in x.data_dict.values():
                seq_list.append(y)
                
        # single runs
        run_list = []
        
        for x in self.single_runs.values():
            run_list.append(x)
            
        all_data_list = seq_list + run_list
        
        return(all_data_list)

        
        #sequence_dict[x].data_dict[y]
        
        #sequence_data = {x.name : x for x in sequence}
        
from datetime import datetime

"""
a prototyped class definition using bits of rainbow and bits of direct XML parsing.

I'll keep building it from here as my use case increases, but it is barebones atm.

"""
    
def main():
    ag = Agilette("/Users/jonathan/0_jono_data/")

    
if __name__ == "__main__":
    
    main()