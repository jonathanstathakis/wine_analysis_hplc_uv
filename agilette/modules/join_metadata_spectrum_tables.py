"""
A module to join a Library object metadata and spectrum tables with loaded spectrum data.
"""

import pandas as pd
import multiprocessing as mp
from function_timer import timeit

# Create a function that will be called by each worker
def worker_func(chunk):
    return chunk.apply(lambda row: (row['spectrum_obj'].extract_spectrum()), axis=1)

@timeit
def spectrum_loader(merge_table : pd.DataFrame) -> pd.DataFrame:

    # Split your DataFrame into chunks for each worker
    chunk_size = mp.cpu_count() * 2  # Adjust the chunk size as needed
    chunks = [merge_table[i:i+chunk_size] for i in range(0, len(merge_table), chunk_size)]
    
    print(f'merge_table split ({merge_table.shape[0]} rows) into', len(chunks), ' chunk(s) for multuprocessing')

    # Create a pool of worker processes

    with mp.get_context('forkserver').Pool(processes=mp.cpu_count()) as pool:

        # Run the worker function for each chunk of data
        results = pool.map(worker_func, chunks)

        # Concatenate the results and assign them to the new column
        merge_table['spectrum'] = pd.concat(results, ignore_index=True)
    
    return merge_table

def join_metadata_spectrum_tables(metadata_table : pd.DataFrame, spectrum_table: pd.DataFrame) -> pd.DataFrame:
    """
    Joins the metadata and spectrum tables on a join_col formed from the acq_date and path columns, then loads the spectrum data into the spectrum objects in the spectrun obj column.

    takes two pandas DataFrames, returns a merged pandas DataFrame.
    """
    print('joining Library.metadata_table with Library.spectrum_table')
    # 1. form the join column

    metadata_table['join_col'] = metadata_table['acq_date'].astype(str) + metadata_table['path'].astype(str)
    spectrum_table['join_col'] = spectrum_table['acq_date'].astype(str) + spectrum_table['path'].astype(str).str.lower()
    
    try:
        merge_table = pd.merge(metadata_table, spectrum_table.drop(['name', 'path', 'acq_date'], axis = 1), on = 'join_col').drop('join_col', axis = 1)

    except Exception as e:
        print(e)

    # 2. load UV data.
    # remove rows that don't contain UV files
    merge_table = merge_table[~(merge_table['uv_filenames'] == 'empty')]

    print("\nloading spectrum into merge_table['spectrum']")
    merge_table = spectrum_loader(merge_table)

    print("spectrum loaded", merge_table[~(merge_table['spectrum'].isna())].shape[0], "rows")

    return merge_table




    