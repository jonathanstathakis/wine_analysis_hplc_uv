"""
This script is intended to assist me in cleaning up the sample tracker website. To enable this I need to:
1. Get the spreadsheet data.
2. Form a dataframe.

Then the primary task will be to form a dataframe and clean up the vintage and name columns so that I can use that list to batch form a cellartracker database, then re-export the selected metedata for statistical analysis.

2023-03-28: task done. Data has been cleaned up and the old values have been replaced. This file is now defunct, but will be kept as a reference.
"""

import pandas as pd

import os

from google_sheets_api import get_sheets_values_as_df, post_df_as_sheet_values, post_new_sheet

def extract_vintage_from_name(df):

    wines_without_vintage_mask = (df['vintage'].isna()) & ~(df['name'].isna()) & ~(df['name'] == 'missing vials') & ~(df['name'] == 'mystery')

    wines_without_vintage = df[wines_without_vintage_mask]

    wines_without_vintage = wines_without_vintage[['id', 'vintage','name']]

    # Find wines where the vintage is held in the first two characters of the name string, split that off, add to vintage column, remove those characters from name column.
    
    match_two_digit_vintage_string = r'(?:\b(\d{2})\w*)?'

    # extract vintage date strings and place in 'vintage' column.

    wines_without_vintage['vintage'] = wines_without_vintage['name'].str.extract(match_two_digit_vintage_string, expand = False)

    # remove the residual vintages from name.

    wines_without_vintage['name'] = wines_without_vintage['name'].str.replace(match_two_digit_vintage_string, "", regex = True)

    # strip residual whitespace

    wines_without_vintage['name'] = wines_without_vintage['name'].apply(lambda x : x.strip())

    # format two digit vintages as 4 digits by adding '20'. Note: be aware of any 20th century wines further down the track..

    wines_without_vintage['vintage'] = wines_without_vintage['vintage'].apply(lambda x : f"20{x}")
    
    # shape = 73 here.
    df.update(wines_without_vintage)

    return df

def values_df_cleaner(df : pd.DataFrame):

    # do the usual cleanup. Lower, strip, check datatypes.

    df = df.apply(lambda x : x.str.lower())
    df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # replace the column names with more approp ones

    # replace cells with empty strings to NaN.

    import numpy as np

    df = df.replace('', np.nan)

    df = df.fillna(value=np.nan)

    df = extract_vintage_from_name(df)

    # remove 4 digit vintages from names.

    df['name'] = df['name'].str.replace(r'\d{4}', "", regex = True)

    return df 

def main():

    creds_path='/Users/jonathan/wine_analysis_hplc_uv/notebooks/credentials_tokens/'

   # in_sheet, in_data_range = ("15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY","sample_tracker!A1:G200")

    df = get_sheets_values_as_df(in_sheet, in_data_range, creds_parent_path=creds_path)

    df = values_df_cleaner(df)

    # add a bottle size column

    df['size'] = '750'

    wynns_mask = df['name'].str.contains('wynns', na = False)
    
    df.loc[wynns_mask,'name'] = 'wynns coonawarra estate shiraz'

    # replace ch with chardonnay, shz with shiraz, pn with pinot noir

    df['name'] = df['name'].replace({' ch$' : ' chardonnay', ' shz$' : ' shiraz', 'pn$' : 'pinot noir'}, regex = True)

    #df = df[df['name'].notna() & df['vintage'].notna()]

    # final strip

    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    df = df.fillna("")

    #sheet_title = 'test_sheet_9000'

    response = post_new_sheet(in_sheet,
                   sheet_title,
                   creds_path)
    
    print(response)

    range = f'{sheet_title}!A1'

    response = post_df_as_sheet_values(df,
                            in_sheet,
                            range,
                            creds_parent_path=creds_path
                            )

    print(f'{response.get("updatedCells")} cells updated.')

main()