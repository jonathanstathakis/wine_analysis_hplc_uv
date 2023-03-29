from typing import Union
from pathlib import Path
import pandas as pd

from agilette.modules.sequence import Sequence
from agilette.modules.library_input_validation import run_input_validation
from agilette.modules.metadata_table import metadata_table
from agilette.modules.run_dir import Run_Dir

class Runs_List:
    def __init__(self, runs : list) -> None:
        self.runs = runs

    
    def __str__(self):
        #return "\n".join(str(run) for run in self.runs)

class Library:
    """
    The equivalent of the top level dir. use .data_table() to view all runs in the data folder path provided, otherwise give a list of .D file names to speed up load times.
    """
    def __init__(self, path : Union[str, list, Path]):
        """
        runs_to_load can be a single filepath string, a Path object, or list of either filepath strings or Path objects. If it is a string, convert it to Path object before continuing.

        If it is a list, iterate through the list and check the file types.
        """
        self.path = path
        self.runs_list = Runs_List(self.load_runs(self.path))
    


    def load_runs(self, path: Union[str, Path, list]) -> list:
        """
        Read in filepaths to Agilent .D run dirs to be used to initialise Run_Dir objs.
        
        Currently this function only wraps run_input_validation, but plans for more functionality later.
        
        Input options are:
        1. Path or str filepath to specific .D.
        2. List of Path or str filepaths to specified .D.
        3. Top level directory containing .D dirs.

        Output is a list of verified path objects leading to .D dirs.
        """
        
        runs = run_input_validation(path)

        try:

            if not isinstance(runs, type(None)):
                
                def run_dir_obj_loader(runs):

                    loaded_runs = [Run_Dir(run) for run in runs]

                    return loaded_runs
                
                runs = run_dir_obj_loader(runs)
            
        except Exception as e:
            print(f"an error occured, {e}")

        return runs
            
                        
    # def sequences(self):
        
    #     sequence_dict = {sequence_dir.name : Sequence(sequence_dir) for sequence_dir in self.path.iterdir() if sequence_dir.name.endswith(".sequence")}
        
    #     return sequence_dict