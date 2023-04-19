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

def selected_avantor_runs(df : pd.DataFrame) -> pd.DataFrame:
    """
    Selects runs to be included in study dataset.
    """
    print(f"Filtering for selected underivatized avantor column runs. df starts with {df.shape[0]} runs")

    print(df['acq_date'])
    
    # select runs from 2023 on the avantor column.

    df = df[(df['acq_date'] > '2023-01-01') & (df['acq_method'].str.contains('avantor'))]

    print(f"after filtering for 2023 runs, {df.shape[0]} runs remaining\n")

    sequences_to_drop = \
        list(df.groupby('sequence_name').filter(lambda x: len(x) == 1).groupby('sequence_name').groups.keys())\
        + df[df['sequence_name'].str.contains('dups')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('repeat')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('44min')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('acetone')]['sequence_name'].unique().tolist()
    
    df = df[df['sequence_name'].isin(sequences_to_drop)==False]

    print(f"after filtering out 'dups', 'repeat', '44min', 'acetone' runs, {df.shape[0]} runs remaining\n")
    
    df = df[~(df['new_id'].str.contains('lor-ristretto'))]
    df = df[~(df['new_id'] == 'uracil')]
    df = df[~(df['new_id'] == 'toulene')]
    df = df[~(df['new_id'].str.contains('acetone'))]
    df = df[~(df['new_id'].str.contains('coffee'))]

    print(f"after filtering out 'lor-ristretto','uracil', 'toulene', 'acetone,'cofee' runs, {df.shape[0]} runs remaining\n")

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

def agilette_library_loader():
    """
    Load the full library metadata table and saves it to a .csv for faster load times, if this is the first time the code is run. ATM does not check for updates, so to get them, will have to delete the .csv and run the code again.
    """
    print("loading inputted library")
    file_name = 'agilette_library.csv'
    file_path = os.path.join(os.getcwd(),file_name)
    
    df = Library('/Users/jonathan/0_jono_data').metadata_table

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
    df = df.astype({
        "vintage" : pd.StringDtype(),
        "id" : pd.StringDtype(),
        "name" : pd.StringDtype(),
        "open_date" : pd.StringDtype(),
        "sampled_date" : pd.StringDtype(),
        "added_to_cellartracker" : pd.StringDtype(),
        "notes" : pd.StringDtype(),
        "size" : np.float64
    })

    df = df_string_cleaner(df)

    return df

def form_join_col(df):
    df['join_key'] = df['vintage'].astype(str) + " " + df['name']
    return df

def chemstation_sample_tracker_join(in_df :pd.DataFrame, sample_tracker_df : pd.DataFrame) -> pd.DataFrame:
    print("## joining metadata table with sample_tracker ##\n")

    print(f"in_df has shape {in_df.shape}, columns {in_df.columns}")
    print(f"sample_tracker_df has shape {sample_tracker_df.shape}")


    sample_tracker_df = sample_tracker_df[['id','vintage', 'name', 'open_date', 'sampled_date', 'notes']]

    merge_df = pd.merge(in_df, sample_tracker_df, left_on ='new_id', right_on = 'id', how = 'left')
    merge_df.attrs['name'] = 'metadata, sample tracker merge table'

    print("df of dims", merge_df.shape, "formed after merge")

    return merge_df

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
    merge_df = pd.merge(df1, df2, left_on='join_key_matched', right_on='join_key', how = 'left', suffixes = ['_ms','_ct'])

    return merge_df

def cellar_tracker_fuzzy_join(in_df : pd.DataFrame, cellartracker_df : pd.DataFrame) -> pd.DataFrame:
    """
    change all id edits to 'new id'. merge sample_tracker on new_id. Spectrum table will be merged on old_id.
    """
    print("joining metadata_table+sample_tracker with cellar_tracker metadata")
    cellartracker_df.attrs['name'] = 'cellar tracker table'
    
    in_df = form_join_col(in_df)
    cellartracker_df = form_join_col(cellartracker_df)

    merge_df = join_dfs_with_fuzzy(in_df, cellartracker_df)

    print("df of dims", merge_df.shape, "formed after merge")
    return merge_df

@timeit 
def super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df):
    
    df = (chemstation_df
        .pipe(chemstation_id_cleaner)
        .pipe(selected_avantor_runs)
        .pipe(chemstation_sample_tracker_join, sample_tracker_df)
        .pipe(cellar_tracker_fuzzy_join,  cellartracker_df)
    )
    return df

def main():
    chemstation_df = agilette_library_loader()
    sample_tracker_df = sample_tracker_df_builder()
    cellartracker_df = get_cellar_tracker_table().convert_dtypes()
    
    print(super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df))

if __name__ == "__main__":
    main()