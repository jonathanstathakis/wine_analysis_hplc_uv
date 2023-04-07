"""
Joins `agilette.Library.metadata_table` with metadata from sample_tracker and cellartracker.

See Users/jonathan/001_obsidian_vault/mres_logbzook/2023-04-06_logbook.md, Users/jonathan/001_obsidian_vault/mres_logbook/2023-04-05_logbook_depicting-progress-thus-far, notebooks/2023-04-05_description-of-dataset-thus-far.ipynb for need, notebooks/2023-03-28-joining-cellartracker-metadata.ipynb for prototype.

1. [x] get sample_tracker table.
2. [] get cellar_tracker table.
3. [x] left join sample_tracker on metadata_table.
4. [ ] left join cellartracker table on metadata table.
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

def sample_tracker_df_builder():

    df = get_sheets_values_as_df(
        spreadsheet_id='15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY',
        range='sample_tracker!A1:H200',
        creds_parent_path="/Users/jonathan/wine_analysis_hplc_uv/agilette/modules/credientals_tokens/")
    return df

def sample_tracker_download():
    file_name = 'sample_tracker.csv'
    file_path = os.path.join(os.getcwd(),file_name)
    if not os.path.exists(file_path):
        df = sample_tracker_df_builder()
        df.to_csv(file_path, index = False)
    else:
        df = pd.read_csv(file_path)
    return df

def agilette_library_loader():
    file_name = 'agilette_library.csv'
    file_path = os.path.join(os.getcwd(),file_name)
    if not os.path.exists(file_path):
        df = Library('/Users/jonathan/0_jono_data').metadata_table
        df.to_csv(file_path, index = False)
    else:
        df = pd.read_csv(file_path)
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

    return cellar_tracker_df

def main():
    metadata_table = agilette_library_loader()

    print('metadata table unique rows :', metadata_table['id'].unique().shape)

    # metadata table starts with 142 unique rows.

    sample_tracker_df = sample_tracker_download().convert_dtypes()

    print('sample_tracker_df table unique rows :', sample_tracker_df['id'].unique().shape)

    # sample_tracker_df starts with 97 unique rows.

    sample_tracker_df = sample_tracker_df[['id','vintage', 'name', 'open_date', 'sample_date', 'variety', 'notes']]

    merge_metadata_sample_tracker = pd.merge(metadata_table, sample_tracker_df, on ='id', how = 'left')

    print('merge_metadata_sample_tracker rows :', merge_metadata_sample_tracker['id'].shape)

    # I approve the contents of merge_metadata_sample_tracker.

    cellartracker_df = get_cellar_tracker_table().convert_dtypes()

    print('cellartracker_df rows :', cellartracker_df['name'].shape)

    def form_join_col(df):
        df['join_key'] = df['vintage'] + " " + df['name']
        return df

    merge_metadata_sample_tracker = form_join_col(merge_metadata_sample_tracker)
    cellartracker_df = form_join_col(cellartracker_df)

    # now, we expect to be able to find every wine in `merge_metadata_sample_tracker` in `cellartracker_df`, however the reverse is not true, and we are expecting many more wines in cellartracker_df than in merge_metadata_sample_tracker, as it is my general wine product repository. So a isin of `merge_metadata_sample_tracker.join_key` should return a frame the same length as `merge_metadata_sample_tracker.join_key`.

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

        merged_df = pd.merge(df1, df2, left_on='join_key_matched', right_on='join_key', how = 'left')

        return merged_df
    
    df = join_dfs_with_fuzzy(merge_metadata_sample_tracker, cellartracker_df)

    df.to_excel(os.path.join(os.getcwd(), 'super_df.xlsx'))

    print(df.groupby(['varietal'])['name_y'].nunique())

    print(df.groupby(['varietal']).get_group('cabernet sauvignon')['join_key_y'].unique())
    
main()