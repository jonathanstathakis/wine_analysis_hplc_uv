"""
Contains spectrum_table, takes a list of lists spectrum objects and metadata to form a primary key, outputs a df.

Exists to store the data objects for data loading before joining with the metadata table.
"""

import pandas as pd

def spectrum_table(spectrum_list : list) -> pd.DataFrame:
    """
    Takes a list of lists containing a spectrum object and metadata for aprimary key, outputs a dataframe.
    """
    column_names = [
        'acq_date',
        'name',
        'path',
        'spectrum_obj'
    ]
    
    df = pd.DataFrame(spectrum_list, columns = column_names)

    #df = df.sort_values('acq_date', ascending = False)

    return df