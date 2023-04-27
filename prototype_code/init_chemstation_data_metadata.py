import duckdb as db
import rainbow as rb
import os
import multiprocessing as mp
import pandas as pd
import numpy as np
import json
import hashlib
import fnmatch
import collections
from function_timer import timeit
from db_methods import display_table_info

def init_raw_chemstation_tables(root_dir_path : str, con : db.DuckDBPyConnection):
    dirpaths = uv_file_dir_filter(root_dir_path)
    print(len(dirpaths), ".D in the given path")
    
    uv_metadata_list, uv_data_list = zip(*uv_extractor_pool(dirpaths))

    print('num of unique hash keys in metadata list')
    
    num_unique_hash = len(set(d['hash_key'] for d in uv_metadata_list))
    print('num unqiue hash keys', num_unique_hash)
    print('size of metadata_list', len(uv_metadata_list))

    list_of_keys = [d['hash_key'] for d in uv_metadata_list]

    uuid_counts = collections.Counter(list_of_keys)

    # print the UUIDs that occur more than once
    duplicates = [uuid for uuid, count in uuid_counts.items() if count > 1]
    print('Duplicate UUIDs:', len(duplicates))

    for uuid in duplicates:
        print(uuid)
        for metadata_dict in uv_metadata_list:
            if uuid == metadata_dict['hash_key']:
                print(metadata_dict['path'])

    metadata_table_builder(uv_metadata_list, con)
    spectrum_table(uv_data_list, con)
    #uv_d ata_table_builder(uv_data_list, con)

def spectrum_table(uv_data_list : list, con : db.DuckDBPyConnection) -> None:

    table_name = 'spectrums'
    con.sql(f"DROP TABLE IF EXISTS {table_name}")

    spectrum_dfs = []
    for uv_data in uv_data_list:
        data = uv_data['data']
        data['hash_key'] = uv_data['hash_key']
        spectrum_dfs.append(data)

    combined_df = pd.concat(spectrum_dfs)

    try:
        print(f'creating {table_name} table from combined_df')
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM combined_df")
    except Exception as e:
        print(e)

    display_table_info(con, table_name)

    return None


def uv_data_to_df(uv_file):
    spectrum = np.concatenate((uv_file.xlabels.reshape(-1,1),uv_file.data), axis = 1)

    column_names = ['mins'] + list(uv_file.ylabels)
    column_names = [str(name) for name in column_names]

    an_index = np.arange(0,spectrum.shape[0])

    try:
        df = pd.DataFrame(data = spectrum, columns = column_names, index = an_index)
        return df
    except Exception as e:
        print(e)
        print(uv_file.metadata.get('notebook'), uv_file.metadata.get('date'))

import uuid

def primary_key_generator(metadata_dict):
    data_json = json.dumps(metadata_dict['date'], sort_keys=True)
    unique_id = uuid.uuid5(uuid.NAMESPACE_URL, data_json)
    return str(unique_id).replace('-','_')


def get_sequence_name(path : str) -> str:
    parent = os.path.dirname(path)
    if 'sequence.acaml' in os.listdir(parent):
        sequence_name = os.path.basename(parent)
    else:
        sequence_name = 'single_run'

    return sequence_name


def uv_extractor(path : str) -> dict:
    
    uv_name = 'DAD1.UV'
    
    if os.path.isfile(os.path.join(path, uv_name)):
        uv_file = rb.read(path).get_file(uv_name)
        
        metadata_dict = uv_file.metadata
        metadata_dict['path'] = path
        metadata_dict['sequence_name'] = get_sequence_name(metadata_dict['path'])
        metadata_dict['hash_key'] = primary_key_generator(metadata_dict)

        uv_data_dict = {}
        uv_data_dict['data'] = uv_data_to_df(uv_file)
        uv_data_dict['hash_key'] = metadata_dict['hash_key']

        return metadata_dict, uv_data_dict

@timeit
def metadata_table_builder(uv_metadata, con):

    table_name = 'raw_chemstation_metadata'
    con.sql(f"DROP TABLE IF EXISTS {table_name}")
    
    df = pd.json_normalize(data = uv_metadata)
    
    try:
        print(f'creating {table_name} table from df')
        con.execute(f"CREATE TABLE {table_name} AS SElECT * FROM df")
    except Exception as e:
        print(e)
    
    display_table_info(con, table_name)

@timeit
def uv_data_table_builder(uv_data_list, con):

    spectrum_table_name_prefix = "hplc_spectrum_"

    print('creating spectrum tables')
    for uv_data in uv_data_list:
        data = uv_data['data']

        try:
            con.sql(f"CREATE TABLE {spectrum_table_name_prefix + str(uv_data['hash_key'])} AS SELECT * FROM data")
        except Exception as e:
            print(e)

    num_unique_hash = len(set(d['hash_key'] for d in uv_data_list))
    print(num_unique_hash, "unique hash keys generated")

    # display result

    num_spectrum_tables = con.sql(f"""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_type='BASE TABLE' AND table_name LIKE '%{spectrum_table_name_prefix}%'
    """).fetchone()[0]
    print(f"{num_spectrum_tables} spectrum tables created with name pattern '[{spectrum_table_name_prefix}]")

@timeit
def uv_file_dir_filter(root_dir_path : str) -> list:
    # Create an empty list to store the matching directory paths
    dirpaths = []

    # Walk through the directory tree using os.walk()
    for dirpath, dirnames, filenames in os.walk(root_dir_path):
        # Check if the directory name ends with '.D'

        if dirpath.endswith('.D'):
            # Check if there is at least one file in the directory that ends with '.UV'
            if any(fnmatch.fnmatch(file, '*.UV') for file in filenames):
                # If both conditions are met, append the directory path to the list
                dirpaths.append(dirpath)

    return dirpaths

@timeit
def uv_extractor_pool(dirpaths) -> list:
    print('processing the given .D directories')
    pool = mp.Pool()
    uv_file_tuples  = pool.map(uv_extractor, dirpaths)
    pool.close()
    pool.join()
    return uv_file_tuples

@timeit
def main():
    root_dir_path = "/Users/jonathan/0_jono_data"
    con = db.connect('uv_database.db')
    init_raw_chemstation_tables(root_dir_path, con)


if __name__ == "__main__":
    main()