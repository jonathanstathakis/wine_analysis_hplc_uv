"""
A module to join a Library object metadata and spectrum tables with loaded spectrum data.
"""

import pandas as pd

def join_metadata_spectrum_tables(metadata_table : pd.DataFrame, spectrum_table: pd.DataFrame) -> pd.DataFrame:
    """
    Joins the metadata and spectrum tables on a join_col formed from the acq_date and path columns, then loads the spectrum data into the spectrum objects in the spectrun obj column.

    takes two pandas DataFrames, returns a merged pandas DataFrame.
    """
    # 1. form the join column

    metadata_table['join_col'] = metadata_table['acq_date'].astype(str) + metadata_table['path'].astype(str)
    spectrum_table['join_col'] = spectrum_table['acq_date'].astype(str) + spectrum_table['path'].astype(str)

    # if metadata_table['join_col'].equals(spectrum_table['join_col']):

    try:
        
        merge_table = pd.merge(metadata_table, spectrum_table.drop(['name', 'path', 'acq_date'], axis = 1), on = 'join_col').drop('join_col', axis = 1)

    except Exception as e:
        print(e)

    # else:
    #     raise ValueError('Attempted merge, but join cols were not equal')

    # 2. load UV data.
    
    merge_table['spectrum'] = merge_table['spectrum_obj'].apply(lambda x : x.extract_spectrum())

    return merge_table




    