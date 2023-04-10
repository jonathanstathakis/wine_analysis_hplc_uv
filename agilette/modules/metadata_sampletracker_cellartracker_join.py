"""
Joins `agilette.Library.metadata_table` with metadata from sample_tracker and cellartracker.

See Users/jonathan/001_obsidian_vault/mres_logbook/2023-04-06_logbook.md, Users/jonathan/001_obsidian_vault/mres_logbook/2023-04-05_logbook_depicting-progress-thus-far, notebooks/2023-04-05_description-of-dataset-thus-far.ipynb for need, notebooks/2023-03-28-joining-cellartracker-metadata.ipynb for prototype.

1. [x] get sample_tracker table.
2. [x] get cellar_tracker table.
3. [x] left join sample_tracker on metadata_table.
4. [x] left join cellartracker table on metadata table.
5. [x] rectify join problems.
"""
import sys
sys.path.append('../')
from agilette.modules.library import Library
from google_sheets_api import get_sheets_values_as_df
import pandas as pd
import os
import datetime
from cellartracker import cellartracker
import html
from fuzzywuzzy import fuzz, process
import streamlit as st
import numpy as np
import io

def string_id_to_digit(df : pd.DataFrame) -> pd.DataFrame:
    """
    Replaces the id of a number of runs with their 2 digit id's as stated in the sample tracker.
    """
    # 1. z3 to 00

    df['id'] = df['id'].replace({'z3':'00'})

    return df

def four_digit_id_to_two_digit(df : pd.DataFrame) -> pd.DataFrame:
    df['id'] = df['id'].apply(lambda x : x[1:3] if len(x)==4 else x)
    return df

def selected_avantor_runs(df : pd.DataFrame) -> pd.DataFrame:
    """
    Selects runs to be included in study dataset.
    """
    # select runs from 2023 on the avantor column.
    print(df.shape)
    df = df[(df['acq_date'] > '2023-01-01') & (df['acq_method'].str.contains('avantor'))]
    print(df.shape)

    sequences_to_drop = \
        list(df.groupby('sequence_name').filter(lambda x: len(x) == 1).groupby('sequence_name').groups.keys())\
        + df[df['sequence_name'].str.contains('dups')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('repeat')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('44min')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('acetone')]['sequence_name'].unique().tolist()
            
    df = df[df['sequence_name'].isin(sequences_to_drop)==False]

    df = df[~(df['id'].str.contains('lor-ristretto'))]
    df = df[~(df['id'] == 'uracil')]
    df = df[~(df['id'] == 'toulene')]
    df = df[~(df['id'].str.contains('acetone'))]
    df = df[~(df['id'].str.contains('coffee'))]

    return df

def df_string_cleaner(df : pd.DataFrame) -> pd.DataFrame:
    df = df.apply(lambda x: x.str.strip().str.lower() if isinstance(x.dtype, pd.StringDtype) else x)
    return df

def sample_tracker_df_builder():
    df = get_sheets_values_as_df(
        spreadsheet_id='15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY',
        range='sample_tracker!A1:H200',
        creds_parent_path="/Users/jonathan/wine_analysis_hplc_uv/agilette/modules/credientals_tokens/")
    return df

def library_id_replacer(df : pd.DataFrame) -> pd.DataFrame:
    replace_dict = {
        '2021-debortoli-cabernet-merlot_avantor|debertoli_cs': '72',
        'stoney-rise-pn_02-21' : '73',
        'crawford-cab_02-21' : '74',
        'hey-malbec_02-21' : '75',
        'koerner-nellucio-02-21' : '76'
                            }

    df['id'] = df['id'].replace(replace_dict, regex = True)

    return df

def agilette_library_loader():
    """
    Load the full library metadata table and saves it to a .csv for faster load times, if this is the first time the code is run. ATM does not check for updates, so to get them, will have to delete the .csv and run the code again.
    """
    file_name = 'agilette_library.csv'
    file_path = os.path.join(os.getcwd(),file_name)
    if not os.path.exists(file_path):
        df = Library('/Users/jonathan/0_jono_data').metadata_table
        df.to_csv(file_path, index = False)
    else:
        df = pd.read_csv(file_path, infer_datetime_format=True)

        df['acq_date'] = pd.to_datetime(df['acq_date'])
    
    df = df.astype({ 
                    "id" : pd.StringDtype(),
                    "path" : pd.StringDtype(),
                    "acq_method" : pd.StringDtype(),
                    "description" : pd.StringDtype(),
                    "program_type" : pd.StringDtype(),
                    "sequence_name" : pd.StringDtype(),
                    "ch_filenames" : pd.StringDtype(),
                    "uv_filenames" : pd.StringDtype()
                    })
    
    df = df_string_cleaner(df)

    df = library_id_replacer(df)

    return df

def get_cellar_tracker_table():

    client = cellartracker.CellarTracker('OctaneOolong', 'S74rg4z3r1')

    usecols = ['Size', 'Vintage', 'Wine', 'Locale', 'Country', 'Region', 'SubRegion', 'Appellation', 'Producer', 'Type', 'Color', 'Category', 'Varietal']

    cellar_tracker_df = pd.DataFrame(client.get_list())
    cellar_tracker_df = cellar_tracker_df[usecols]

    # clean it up. lower values and columns, replace 1001 with nv, check datatypes

    cellar_tracker_df = cellar_tracker_df.apply(lambda x : x.str.lower() if str(x) else x)
    cellar_tracker_df.columns = cellar_tracker_df.columns.str.lower()
    cellar_tracker_df = cellar_tracker_df.rename({'wine' : 'name'}, axis = 1)

    cellar_tracker_df = cellar_tracker_df.replace({'1001' : 'nv'})

    def unescape_html(s):
        return html.unescape(s)

    cellar_tracker_df = cellar_tracker_df.applymap(unescape_html)


    cellar_tracker_df = df_string_cleaner(cellar_tracker_df)

    return cellar_tracker_df

def st_df_info(df : pd.DataFrame) -> pd.DataFrame:
    
    info_df = pd.DataFrame()
    info_df['types'] = df.dtypes
    info_df['NA'] = df.isnull().sum()

    st.title(df.attrs['name'])
    st.header('df shape and size')
    st.write(f"shape: {df.shape} | size: {df.size}")

    with st.container():
        st.header('df columns')
        st.table(info_df.astype(str))
            
    with st.container():
        st.header(f"{df.attrs['name']} head")
        st.write(df.head().astype(str))

def sample_tracker_download():
    """
    Downloads the sample tracker file as a .csv for faster load times. ATM does not check the Google Sheet for changes so will need to manually delete the file to get updates.
    """
    file_name = 'sample_tracker.csv'
    file_path = os.path.join(os.getcwd(),file_name)
    df = sample_tracker_df_builder()
    if not os.path.exists(file_path):
        df.to_csv(file_path, index = False)
    else:
        df = pd.read_csv(file_path)
    
    df = df.astype({
        "vintage" : pd.StringDtype(),
        "id" : pd.StringDtype(),
        "name" : pd.StringDtype(),
        "open_date" : pd.StringDtype(),
        "sample_date" : pd.StringDtype(),
        "added_to_cellartracker" : pd.StringDtype(),
        "notes" : pd.StringDtype(),
        "size" : np.float64
    })

    df = df_string_cleaner(df)

    return df

def join_dfs_with_fuzzy(df1 : pd.DataFrame, df2 : pd.DataFrame) -> pd.DataFrame:
    
    def fuzzy_match(s1, s2):
        return fuzz.token_set_ratio(s1, s2)

    df1 = df1.fillna('empty')
    df2 = df2.fillna('empty')

    df1['join_key_match'] = df1['join_key'].apply(lambda x: process.extractOne(x, df2['join_key'], scorer = fuzzy_match))

    # the above code produces a tuple of: ('matched_string', 'match score', 'matched_string_indice'). Usually it's two return values, but using scorer=fuzzy.token_sort_ratio or scorer=fuzz.token_set_ratio returns the index as well.

    df1['join_key_matched'] = df1['join_key_match'].apply(lambda x: x[0] if x[1] > 65 else None)
    df1['join_key_similarity'] = df1['join_key_match'].apply(lambda x : x[1] if x[1] > 65 else None)

    df1.drop(columns = ['join_key_match'], inplace = True)

    # 'ms' indicates column was sourced from metadata-sampletracker table, 'ct' from cellartracker table.
    merged_df = pd.merge(df1, df2, left_on='join_key_matched', right_on='join_key', how = 'left', suffixes = ['_ms','_ct'])

    return merged_df

def agilent_sample_tracker_cellartracker_super_table():
    metadata_df = agilette_library_loader()
    metadata_df.attrs['name'] = 'metadata in attrs'
    st_df_info(metadata_df)

    avantor_df = selected_avantor_runs(metadata_df)
    avantor_df = four_digit_id_to_two_digit(avantor_df)
    avantor_df = string_id_to_digit(avantor_df)

    sample_tracker_df = sample_tracker_download()
    sample_tracker_df.attrs['name'] = 'sample tracker'
    sample_tracker_df = sample_tracker_df[['id','vintage', 'name', 'open_date', 'sample_date', 'notes']]
    st_df_info(sample_tracker_df)

    merge_metadata_sample_tracker = pd.merge(avantor_df, sample_tracker_df, on ='id', how = 'left')
    merge_metadata_sample_tracker.attrs['name'] = 'metadata, sample tracker merge table'
    st_df_info(merge_metadata_sample_tracker)

    cellartracker_df = get_cellar_tracker_table().convert_dtypes()
    cellartracker_df.attrs['name'] = 'cellar tracker table'
    st_df_info(cellartracker_df)
    
    def form_join_col(df):
        df['join_key'] = df['vintage'] + " " + df['name']
        return df

    merge_metadata_sample_tracker = form_join_col(merge_metadata_sample_tracker)
    cellartracker_df = form_join_col(cellartracker_df)
    
    super_table = join_dfs_with_fuzzy(merge_metadata_sample_tracker, cellartracker_df)
    super_table.attrs['name'] = 'final table'
    st_df_info(super_table)

    st.subheader('super table\njoin_key_matched missing values')
    super_table[super_table['join_key_matched'].isna()]

    st.subheader('Super Table')
    super_table[['acq_date','id','join_key_similarity','join_key_ms', 'join_key_matched']]

    st.subheader('cellartracker debortoli')
    cellartracker_df[cellartracker_df['name'].str.contains('debortoli')]

    return super_table