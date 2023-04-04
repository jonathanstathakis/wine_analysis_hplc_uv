"""
Generates a metadata table from a given metadata_list.

Only for use from a Library object loading metadata from its Run_Dir objects.

List of lists as input, pd.DataFrame as output.
"""

import pandas as pd

def metadata_table(metadata_list : list) -> pd.DataFrame:
        """
        list of lists of metadata as input, dataframe as output. Nonstandalone function of Library.
        """
        column_names = ['acq_date',
                   'id',
                   'path',
                   'acq_method',
                   'description',
                   'sequence_name',
                   'ch_filenames',
                   'uv_filenames'
                   ]
        
        df = pd.DataFrame(metadata_list, columns= column_names)
        
        df = df.sort_values('acq_date', ascending = False)

        return df