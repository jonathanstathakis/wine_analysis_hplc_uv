# spectrum_df['signal_shape'] = spectrum_df.apply(lambda row : row[wavelength].shape, axis = 1)
# spectrum_df['signal_index'] = spectrum_df.apply(lambda row : row[wavelength].index.tolist(), axis = 1)
# spectrum_df['signal_columns'] = spectrum_df.apply(lambda row : row[wavelength].columns.tolist(), axis = 1)

"""
Contains general df methods to improve quality of life when working with pandas dataframes.
"""

import pandas as pd

def describe_df(df : pd.DataFrame):
    print("df shape:", df.shape)
    print("df columns", df.columns)
    print("df index", df.index)

    return None