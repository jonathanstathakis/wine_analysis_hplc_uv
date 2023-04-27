"""
A file to contain a number of general pandas dataframe cleaning methods.
"""
import pandas as pd

def df_string_cleaner(df : pd.DataFrame) -> pd.DataFrame:
        def lowercase_and_strip(value):
                if isinstance(value, str):

                        return value.lower().strip()
                return value
        print('lowering case and stripping all str columns in df')
        df = df.applymap(lowercase_and_strip)
        
        return df