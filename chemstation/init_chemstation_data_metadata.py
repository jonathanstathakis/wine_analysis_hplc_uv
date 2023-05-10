"""
todo:
- [ ] change db connections to be context managed only at the point of writing, pass the db filepath rather than the conn object.
"""

from devtools import project_settings
import duckdb as db
import rainbow as rb
import sys
import os
import multiprocessing as mp
import pandas as pd
import numpy as np
import json
import fnmatch
import collections
from devtools import function_timer as ft
from db_methods import db_methods
from chemstation import chemstation_to_db_methods
from chemstation import chemstation_methods

counter = None
counter_lock = None

def init_chemstation_data_metadata_tables(data_lib_path : str, con : db.DuckDBPyConnection):
    """
    main driver file, handle any preprocessing then activate write_ch_metadata_table_to_db.
    """
    print(f"processing dirs at {data_lib_path}..")
    uv_paths_list = chemstation_methods.uv_filepaths_to_list(data_lib_path)
    uv_metadata_list, uv_data_list = ch_dirs_to_dict_lists(uv_paths_list, con)
    chemstation_to_db_methods.write_ch_metadata_table_to_db(uv_metadata_list, con)
    chemstation_to_db_methods.write_spectrum_table_to_db(uv_data_list, con)
    return None

def ch_dirs_to_dict_lists(dirpath_list : list, con : db.DuckDBPyConnection):
    """
    1. Create the metadata and data dicts from each .D file.
    2. check that the hash keys are unique.
    3. return uv_metadata_list and uv_data_list
    """
    if isinstance(dirpath_list, list):
        
        if input("Overwrite raw chemstation tables in db? (y/n):") == "y":
            # extract the metadata and data from each .D file as a list of a tuple of dicts.

            uv_file_pool = uv_extractor_pool(dirpath_list)

            try:
                uv_metadata_list, uv_data_list = zip(*uv_file_pool)
            except TypeError as e:
                print(f"Tried to unpack uv_file_pool but {e}")
                sys.exit()

            duplicate_hash_keys(uv_metadata_list)
        else:
            print("Leaving raw chemstation tables asis.")
    else:
        print(f"dirpath_list must be list, is {type(dirpath_list)}. Exiting.")
        raise TypeError
    
    return uv_metadata_list, uv_data_list

def duplicate_hash_keys(uv_metadata_list : list):
    # observe how many unique hash_keys were generated. duplicates are probably caused by duplicate files/filenames.
    num_unique_hash = len(set(d['hash_key'] for d in uv_metadata_list))
    print('num unqiue hash keys', num_unique_hash)
    print('size of metadata_list', len(uv_metadata_list))
    
    # print the UUIDs that occur more than once.
    list_of_keys = [d['hash_key'] for d in uv_metadata_list]
    uuid_counts = collections.Counter(list_of_keys)
    duplicates = [uuid for uuid, count in uuid_counts.items() if count > 1]
    print('Duplicate UUIDs:', len(duplicates))

    for uuid in duplicates:
        print(uuid)
        for metadata_dict in uv_metadata_list:
            if uuid == metadata_dict['hash_key']:
                print(f"duplicate UUID generated by: {metadata_dict['path']}")
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

def init_pool(c, l):
    global counter, counter_lock
    counter = c
    counter_lock = l

def uv_extractor(path : str) -> tuple:
    """
    Form two dicts linked by a hash_key for each chemstation .D dir, representing a run.
    Takes a filepath as a str, returns a tuple of dicts, metadata_dict and uv_data_dict.
    
    metadata_dict contains 'path', 'sequence_name', 'hash_key' items. uv_data_dict contains 'data' and 'hash_key' items.
    """
    uv_name = 'DAD1.UV'
    global counter, counter_lock
    
    if os.path.isfile(os.path.join(path, uv_name)):
        uv_file = rb.read(path).get_file(uv_name)
        
        metadata_dict = uv_file.metadata
        metadata_dict['path'] = path
        metadata_dict['sequence_name'] = get_sequence_name(metadata_dict['path'])
        metadata_dict['hash_key'] = primary_key_generator(metadata_dict)

        uv_data_dict = {}
        uv_data_dict['data'] = uv_data_to_df(uv_file)
        uv_data_dict['hash_key'] = metadata_dict['hash_key']

        with counter_lock:
            counter.value += 1
            print(f"Processed {metadata_dict['path']}. Have processed {counter.value} files.")
    else:
        print(f"{path} does not contain a .UV file. Remove from the library?")

        return metadata_dict, uv_data_dict

@ft.timeit
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

@ft.timeit
def uv_extractor_pool(dirpaths: list) -> tuple:
    """
    Form a multiprocess pool to apply uv_extractor, returning a tuple of dicts for each .D file in the dirpath list.
    """
    global counter, counter_lock
    counter = mp.Value('i', 0)  # 'i' indicates an integer
    counter_lock = mp.Lock()

    print("Initializing multiprocessing pool...")
    pool = mp.Pool(initializer=init_pool, initargs=(counter, counter_lock))

    print(f"Processing {len(dirpaths)} directories using a multiprocessing pool...")
    uv_file_tuples = pool.map(uv_extractor, dirpaths)

    print("Closing and joining the multiprocessing pool...")
    pool.close()
    pool.join()

    print("Finished processing files.")
    return uv_file_tuples

@ft.timeit
def main():
    root_dir_path = "/Users/jonathan/0_jono_data"
    con = db.connect('uv_database.db')
    init_chemstation_data_metadata_tables(root_dir_path, con)

if __name__ == "__main__":
    main()