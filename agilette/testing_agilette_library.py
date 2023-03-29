from agilette_core import Library

from pathlib import Path

"""
Cases to test when running Library.load_runs.

1. a string is passed to the library.
2. a path object is passed to the library.
3. a list of strings is passed to the library.
4. a list of Path objects is passed to the library.
5. A mix of dataypes in a list is passed the library (? mayb just reject.)
"""

import time

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.5f} seconds")
        return result
    return wrapper

def test_runs_list_contents(runs: list):
            try:
                if isinstance(runs, list):
                    for run in runs:
                        if not isinstance(run, Path):
                            raise TypeError(f"test failed, {run} is not a Path")
                        if not run.is_dir():
                            raise TypeError(f"test failed, {run} is not a directory")
                        if not run.suffix.endswith(".D"):
                            raise ValueError(f"test failed, {run} is not a run dir")
                
                    print(f'test passed, all contents of runs are Path objects leading to directories that are run dirs.')

                else:
                    raise TypeError(f'{runs} is not a list')
            except Exception as e:
                 print(e)

def test_function():

    # 1. top level dir path
    def test_one_top_dir_with_D(path):
        print(f'{test_one_top_dir_with_D.__name__}')
        lib = Library(path)
        test_runs_list_contents(lib.runs)

        # test for issues
    
    def test_two_dir_without_D(path):
        print(f"{test_two_dir_without_D.__name__}")
        lib = Library(path)
        test_runs_list_contents(lib.runs)

    def test_three_list_of_D(path):
        print(f"{test_three_list_of_D.__name__}")
        lib = Library(path)
        test_runs_list_contents(lib.runs)

    def test_four_a_integer():
         print(f"{test_four_a_integer.__name__}")
         lib = Library(5)
         test_runs_list_contents(lib.runs)


    #test_one_top_dir_with_D(Path('/Users/jonathan/0_jono_data/'))

    test_two_dir_without_D(Path('/Users/jonathan/wine_analysis_hplc_uv/test_dir_empty'))
    
    test_three_list_of_D(['/Users/jonathan/0_jono_data/2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D','/Users/jonathan/0_jono_data/2023-02-22_KOERNER-NELLUCIO-02-21.D', '/Users/jonathan/0_jono_data/2023-02-16_0291.D'])

    # try 1 string path in a list

    test_three_list_of_D(['/Users/jonathan/0_jono_data/2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D'])

    test_four_a_integer()

test_function()