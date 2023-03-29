from typing import Union
from pathlib import Path
import pandas as pd

from agilette.modules.sequence import Sequence

class Library:

    """
    The equivalent of the top level dir. use .data_table() to view all runs in the data folder path provided, otherwise give a list of .D file names to speed up load times.
    TODO: test behavior of various argument inputs i.e. sequences, single runs, runs_to_load, and combinations. What will happen if there is an overlap?

    2023-03-29 - Going to rework the Library
    """
    def __init__(self, path : Union[str, list, Path]):
        """
        runs_to_load can be a single filepath string, a Path object, or list of either filepath strings or Path objects. If it is a string, convert it to Path object before continuing.

        If it is a list, iterate through the list and check the file types.
        """
        self.path = path
        self.runs = self.load_runs(self.path)

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
        def run_input_validation(path : Union[str, Path, list]) -> list:
            """
            Driver function of load_runs, takes str or Path leading to .D directory or a top level directory containing .D, or a list of both (or either) and returns a list of verified Path objects. 
            
            Throws an error if the input is not one of these three, or if the directory is not a .D, or if the list is empty.

            Note: have not tested what happens if a list contains a directory containing .D objects.
            """

            runs = None

            def path_list_validation(path : list) -> list:
                """
                Takes a list of possible run Dir (.D) paths and valdiates them.

                Takes a list, returns a list.
                """
                try:
                    runs = []
                    for p in path:
                        # 1. test if p is a string, if so convert to Path
                        # 2. test if p is a directory that ends with .D
                        # 3. if one element is not a .D dir, break the loop,
                        if isinstance(p, str):
                            p = Path(p)
                        if p.is_dir() and p.suffix.endswith('.D'):
                            runs.append(p)
                            continue
                        else:
                            # If any item in the list is a file or non-existent path, raise an error
                            raise ValueError(f"{p} is not a directory")
                
                except Exception as e:
                    print(e)
                    return None

                return runs

            try:
                ##3. A list of .D paths
                
                # 1. if its a list, check each element in list.
                # 2. if element is string, turn into Path object.
                # 3. if path leads to dir and the dir is .D, continue to next element.
                # 4. 

                # 1. list
                if isinstance(path, list):
                    runs = path_list_validation(path)
                    return runs

                # 2. if not a list, test for string. if string, turn into Path.
                elif isinstance(path, str):
                    path = Path(path)

                # 3. Now that any strings are caught and converted to Paths, 
                if isinstance(path, Path) and path.is_dir():
                    # single .D path
                    if path.suffix.endswith('.D'):
                        runs = [path]

                    # 4. top level path containing .D dirs.
                    else:
                        runs = [p for p in path.glob('**/*.D')]
                        if not runs:
                            raise ValueError(f"{path} does not contain .D directories")
                else:
                    raise TypeError(f"{path} is not list or Path leading to a directory, it is {type(path)}")

            except Exception as e:
                print(f"An error occurred: {e}")
                
                return None
            
            return runs
        
        runs = run_input_validation(path)
         
        return runs
            
                        
    # def sequences(self):
        
    #     sequence_dict = {sequence_dir.name : Sequence(sequence_dir) for sequence_dir in self.path.iterdir() if sequence_dir.name.endswith(".sequence")}
        
    #     return sequence_dict
    
    def get_all_data_files(self):
            
        import re

        for x in self.path.glob('**/*.D'):
        
            print(x.names)

    
    def data_table(self):

        """
        modify this to be applicable to any set of loaded runs in dict form.
        """
                # need to form dicts for each column then combine them together into the DF. Its just gna display the objects of each data object. Q is though, from what list? self.data_file_dir Also I need to find a way to get the acq date without using rainbow.
        
        
        #ids = [idx for idx, x in enumerate(self.all_data_files)]
        #print([x.acq_date for x in list(self.loaded_runs.values())])

        df = pd.DataFrame({
                          "acq_date" : [x.acq_date for x in self.loaded_runs.values()],
                           "sample_name" : [x.name for x in self.loaded_runs.values()],
                           "run_name" : [x.path.name for x in self.loaded_runs.values()],
                           "path" : [x.path for x in self.loaded_runs.values()],
                           "sequence" : [x.sequence_name for x in self.loaded_runs.values()],
                           "ch_files" : [x.data_files_dict['ch_files'] for x in self.loaded_runs.values()],
                           "uv_files" : [x.data_files_dict['uv_files'] for x in self.loaded_runs.values()],
                           "method" : [x.acq_method for x in self.loaded_runs.values()],
                           "desc" : [x.description for x in self.loaded_runs.values()],
                           "run_dir_obj" : [x for x in self.loaded_runs.values()]
                           
        })

        df = df.sort_values('acq_date', ascending = False).reset_index(drop = True)
        
        return df