import pandas as pd

def masker(df : pd.DataFrame) -> pd.DataFrame:

    df = df[(df['uv_filenames']!='') & (df['acq_method'].str.contains('AVANTOR')) & ~(df['id'].str.contains('uracil')) & ~(df['id'].str.contains('coffee')) & ~(df['id'].str.contains('lor'))]

    return df