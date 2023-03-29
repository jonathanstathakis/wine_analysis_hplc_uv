"""
`Contains run_input_validation()`, a function for ensuring that Library path input is valid .D or a container of .D dirs.
"""

from typing import Union
from pathlib import Path

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