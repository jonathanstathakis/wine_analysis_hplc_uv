"""
Joins `agilette.Library.metadata_table` with metadata from sample_tracker and cellartracker.

2023-04-13-15-40: Import agilent_sample_tracker_cellartracker_super_table to get the subst of MRes thesis usable runs.

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
from cellartracker import cellartracker
import html
from fuzzywuzzy import fuzz, process
import numpy as np
from function_timer import timeit


def string_id_to_digit(df : pd.DataFrame) -> pd.DataFrame:
    """
    Replaces the id of a number of runs with their 2 digit id's as stated in the sample tracker.
    """
    # 1. z3 to 00
    df['new_id'] = df['new_id'].replace({'z3':'00'})
    return df

def four_digit_id_to_two_digit(df : pd.DataFrame) -> pd.DataFrame:
    df = df.rename({'id' : 'old_id'}, axis = 1)
    df['new_id'] = df['old_id'].apply(lambda x : x[1:3] if len(x)==4 else x)
    return df

def selected_avantor_runs(df : pd.DataFrame) -> pd.DataFrame:
    """
    Selects runs to be included in study dataset.
    """
    print("Filtering for selected underivatized avantor column runs")
    # select runs from 2023 on the avantor column.
    df = df[(df['acq_date'] > '2023-01-01') & (df['acq_method'].str.contains('avantor'))]

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
        creds_parent_path=os.environ.get('GOOGLE_SHEETS_API_CREDS_PARENT_PATH'))
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
    print("loading inputted library")
    file_name = 'agilette_library.csv'
    file_path = os.path.join(os.getcwd(),file_name)
    if not os.path.exists(file_path):
        df = Library('/Users/jonathan/0_jono_data').metadata_table
        df.to_csv(file_path, index = False)
    else:
        df = pd.read_csv(file_path)

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

def form_join_col(df):
    df['join_key'] = df['vintage'] + " " + df['name']
    return df

def chemstation_id_cleaner(df : pd.DataFrame) -> pd.DataFrame:
    print("cleaning chemstation run id's")
    df = four_digit_id_to_two_digit(df)
    df = string_id_to_digit(df)
    return df

def chemstation_sample_tracker_join(df :pd.DataFrame) -> pd.DataFrame:
    print("joniing Library.metadata_table with sample_tracker sheet")
    sample_tracker_df = sample_tracker_download()
    sample_tracker_df.attrs['name'] = 'sample tracker'
    sample_tracker_df = sample_tracker_df[['id','vintage', 'name', 'open_date', 'sample_date', 'notes']]

    join_df = pd.merge(df, sample_tracker_df, left_on ='new_id', right_on = 'id', how = 'left')
    join_df.attrs['name'] = 'metadata, sample tracker merge table'
    return join_df

def cellar_tracker_fuzzy_join(df : pd.DataFrame) -> pd.DataFrame:
    """
    change all id edits to 'new id'. merge sample_tracker on new_id. Spectrum table will be merged on old_id.
    """
    print("joining metadata_table+sample_tracker with cellar_tracker metadata")
    cellartracker_df = get_cellar_tracker_table().convert_dtypes()
    cellartracker_df.attrs['name'] = 'cellar tracker table'
    
    df = form_join_col(df)
    cellartracker_df = form_join_col(cellartracker_df)

    df = join_dfs_with_fuzzy(df, cellartracker_df)
    df.attrs['name'] = 'super table'
    return df

@timeit 
def super_table_pipe():
    df = agilette_library_loader()
    df = (df.pipe(selected_avantor_runs)
        .pipe(chemstation_id_cleaner)
        .pipe(chemstation_sample_tracker_join)
        .pipe(cellar_tracker_fuzzy_join)
    )
    return df