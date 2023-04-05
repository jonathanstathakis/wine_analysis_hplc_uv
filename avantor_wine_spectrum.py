import pandas as pd

def masker(df : pd.DataFrame) -> pd.DataFrame:

    df = df[(df['uv_filenames']!='') & (df['acq_method'].str.contains('AVANTOR')) & ~(df['name'].str.contains('uracil')) & ~(df['name'].str.contains('coffee')) & ~(df['name'].str.contains('lor'))]

    return df

/Users/jonathan/wine_analysis_hplc_uv/notebooks/avantor_wine_spectrum.py