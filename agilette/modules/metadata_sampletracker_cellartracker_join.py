"""
Joins `agilette.Library.metadata_table` with metadata from sample_tracker and cellartracker.

2023-04-13-15-40: Import agilent_sample_tracker_cellartracker_super_table to get the subst of MRes thesis usable runs.

See Users/jonathan/001_obsidian_vault/mres_logbook/2023-04-06_logbook.md, Users/jonathan/001_obsidian_vault/mres_logbook/2023-04-05_logbook_depicting-progress-thus-far, notebooks/2023-04-05_description-of-dataset-thus-far.ipynb for need, notebooks/2023-03-28-joining-cellartracker-metadata.ipynb for prototype.
"""
import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
from agilette.modules.library import Library
from google_sheets_api import get_sheets_values_as_df
import pandas as pd
import os
from cellartracker import cellartracker
import html
from fuzzywuzzy import fuzz, process
import numpy as np
from function_timer import timeit
import sample_tracker_methods

def metadata_sampletracker_cellartracker_join():
    chemstation_df = agilette_library_loader()
    sample_tracker_df = sample_tracker_methods.sample_tracker_df_builder()
    cellartracker_df = get_cellar_tracker_table().convert_dtypes()
    super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df)
    return None

def selected_avantor_runs(df : pd.DataFrame) -> pd.DataFrame:
    """
    Selects runs to be included in study dataset.
    """
    print(f"Filtering for selected underivatized avantor column runs. df starts with {df.shape[0]} runs")

    df = df[(df['acq_date'] > '2023-01-01')]
            
    print(f"after filtering for 2023 runs, {df.shape[0]} runs remaining\n")
    
    print(f"Filtering for avantor method runs, {df.shape[0]} runs remaining. Removing:\n{df[~(df['acq_method'].str.contains('avantor'))]}\n")
    
    df = df[df['acq_method'].str.contains('avantor')]

    sequences_to_drop = \
        list(df.groupby('sequence_name').filter(lambda x: len(x) == 1).groupby('sequence_name').groups.keys())\
        + df[df['sequence_name'].str.contains('dups')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('repeat')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('44min')]['sequence_name'].unique().tolist()\
        + df[df['sequence_name'].str.contains('acetone')]['sequence_name'].unique().tolist()
    
    sequence_drop_mask = df['sequence_name'].isin(sequences_to_drop)==False
    print(f"Filtering out 'dups', 'repeat', '44min', 'acetone' runs, {df.shape[0]} runs remaining. Removing:\n\n{df[~sequence_drop_mask].groupby('sequence_name').size()}")
    
    df = df[sequence_drop_mask]

    return df

def df_string_cleaner(df : pd.DataFrame) -> pd.DataFrame:
    df = df.apply(lambda x: x.str.strip().str.lower() if isinstance(x.dtype, pd.StringDtype) else x)
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
    
    # df = df_string_cleaner(df)
    # df = library_id_replacer(df)
    return df

def get_cellar_tracker_table():
    client = cellartracker.CellarTracker('OctaneOolong', 'S74rg4z3r1')

    usecols = ['Size', 'Vintage', 'Wine', 'Locale', 'Country', 'Region', 'SubRegion', 'Appellation', 'Producer', 'Type', 'Color', 'Category', 'Varietal']

    cellar_tracker_df = pd.DataFrame(client.get_list())
    cellar_tracker_df = cellar_tracker_df[usecols]

    # clean it up. lower values and columns, replace 1001 with nv, check datatypes

    
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
    print("\n########\njoining metadata table with sample_tracker\n########")

    print(f"\nin_df has shape: {in_df.shape}\n\tcolumns: {str(list(in_df.columns))}")
    print(f"\nsample_tracker_df has shape {sample_tracker_df.shape}")

    sample_tracker_df = sample_tracker_df[['id','vintage', 'name', 'open_date', 'sampled_date', 'notes']]

    merge_df = pd.merge(in_df, sample_tracker_df, left_on ='new_id', right_on = 'id', how = 'inner')

    print("\ndf of dims", merge_df.shape, "formed after merge of chemstation_metadata and sample_tracker.\n If this df has more rows than the inital left_df, it is because there were duplicate matches, so the rows were duplicated.")

    return merge_df

def join_dfs_with_fuzzy(df1 : pd.DataFrame, df2 : pd.DataFrame) -> pd.DataFrame:
    
    def fuzzy_match(s1, s2):
        return fuzz.token_set_ratio(s1, s2)

    try:
        df1 = df1.fillna('empty')
        df2 = df2.fillna('empty')
    except Exception as e:
        print(f'tried to fill empties in both dfs but {e}')

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
        .pipe(selected_avantor_runs)
        .pipe(chemstation_sample_tracker_join, sample_tracker_df)
        .pipe(cellar_tracker_fuzzy_join,  cellartracker_df)
    )
    return df

def main():
    metadata_sampletracker_cellartracker_join()

if __name__ == "__main__":
    main()