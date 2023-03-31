from typing import Union
from pathlib import Path
import pandas as pd
import inspect

from agilette.modules.sequence import Sequence
from agilette.modules.library_input_validation import run_input_validation
from agilette.modules.metadata_table import metadata_table
from agilette.modules.spectrum_table import spectrum_table
from agilette.modules.join_metadata_spectrum_tables import join_metadata_spectrum_tables
from agilette.modules.run_dir import Run_Dir

class Library:

    """
    The equivalent of the top level dir. use .data_table() to view all runs in the data folder path provided, otherwise give a list of .D file names to speed up load times.
    """
    def __init__(self, path : Union[str, list, Path]):
        """
        runs_to_load can be a single filepath string, a Path object, or list of either filepath strings or Path objects. If it is a string, convert it to Path object before continuing.

        If it is a list, iterate through the list and check the file types.

        TODO: Add something to handle the case if a top-level filepath is passed that is not a correct path.
        """
        self.path = path
        self.runs_list = self.load_runs(self.path)
        self.metadata_list = self.get_metadata_list(self.runs_list)
        self.metadata_table = self.get_metadata_table(self.metadata_list)
        self.spectrum_list = self.get_spectrum_list(self.runs_list)
        self.spectrum_table = self.get_spectrum_table(self.spectrum_list)

    def load_spectrum(self):
        """
        join the `spectrum_table` with `metadata_table` and load the data within the `Spectrum` objects.
        
        Returns a dataframe of the merged tables.
        """
        return join_metadata_spectrum_tables(self.metadata_table, self.spectrum_table)

    def get_spectrum_table(self, spectrum_list : list) -> pd.DataFrame:
        return spectrum_table(spectrum_list)
     
    def get_spectrum_list(self, runs_list : list) -> list:
        spectrum_list = [run.spectrum_to_list() for run in runs_list]
        return spectrum_list
    
    def get_metadata_list(self, runs_list : list) -> list:
        """
        Takes a list of Run_Dir objects and returns a list of their metadata as a list of lists.
        """
        metadata_list = [run.metadata_to_list() for run in runs_list]
        return metadata_list

    def get_metadata_table(self, metadata_list : list) -> pd.DataFrame:
        """
        Takes a list of lists of Library Run_Dir metadata and returns them as a dataframe, using `metadata_table()`
        """
        return metadata_table(metadata_list)


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

                    try:
                        loaded_runs = [Run_Dir(run) for run in runs]
                    except Exception as e:
                        print(f'Error occured in {inspect.currentframe().f_code.co_name} in {Library.__name__}: {e}')

                    return loaded_runs
                
                runs = run_dir_obj_loader(runs)
            
        except Exception as e:
            print(f"an error occured in {inspect.currentframe().f_code.co_name}, {e}")

        return runs
    
    def __str__(self):
        """
        Outputs the path of each run in the Library as an identifier.
        """
        return "Runs in Library:\n" + "\n".join([str(run.path) for run in self.runs_list])
            
                        
    # def sequences(self):
        
    #     sequence_dict = {sequence_dir.name : Sequence(sequence_dir) for sequence_dir in self.path.iterdir() if sequence_dir.name.endswith(".sequence")}
        
    #     return sequence_dict