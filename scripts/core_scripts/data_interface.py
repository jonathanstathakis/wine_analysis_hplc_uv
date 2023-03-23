from datetime import datetime

import pandas as pd

import rainbow as rb

from pathlib import Path

import numpy as np

def acq_method(data_directory):
    return data_directory.datafiles[0].metadata['method']


def data_table(top_dir):
    """
    Takes a pathlib Path object path to the top level directory containing .D (and soon  .sequence) dirs and returns a df of basic info and associated data object for further computation.
    """
    
    top_dir_d = {}

    top_dir_d["name"] = []
    top_dir_d["data"] = []
    top_dir_d["num_detect_files"] = []
    top_dir_d["method"] = []
    top_dir_d["acquisition_date"] = []

    for obj in top_dir.iterdir():
        if obj.name.endswith(".D"):
            try:

                data = rb.read(str(obj))

                top_dir_d["name"].append("_".join(obj.name.split("_")[1:]))
                top_dir_d["data"].append(data)
                top_dir_d["num_detect_files"].append(len(data.datafiles))
                top_dir_d["method"].append(acq_method(data))
                top_dir_d["acquisition_date"].append(datetime.strptime(data.metadata['date'], "%d-%b-%y, %H:%M:%S"))

            except Exception as e:
                print(obj.name, e)

                continue

    df = pd.DataFrame(top_dir_d, index = top_dir_d["name"])

    df = df.set_index('name')
    
    return df

def retrieve_uv_data(uv_data_path : str):

    """
    Takes a rainbow-api DataFile object containing chemstation .UV data and returns a df in
    wide format. For 3d plotting, convert to long format.
    """
    if isinstance(uv_data_path, str):
        data_uv = rb.agilent.chemstation.parse_uv(uv_data_path)

    else:
        print(f'not a string, {type(uv_data_path)}')
    try:

        data = data_uv.data
        time = data_uv.xlabels.reshape(-1,1)
    
    except Exception as e:
        print(e)
    
    try:
        # need to combine the time data with the abs data prior to forming the DF.
        
        combo_data = np.concatenate((time, data), axis = 1)

    except Exception as e:
        
        print(f"trying to form a combination data of time and absorbance but {e}")

    try:
        # form a list of column names to align with the combo_data aray
        
        column_names = ['mins'] + list(data_uv.ylabels)
        
        df = pd.DataFrame(data = combo_data, columns = column_names)
        
        df.columns = df.columns.astype(str)

        df.name = str(f"{Path(uv_data_path).parent.name.replace('.D', '')}_spectrum")
        
    except Exception as e:
        print(e)

    try:
        if isinstance(df, pd.DataFrame):
            return df
        else:
            print('returning nothing, not a DF')
            return df
    
    except Exception as e:
        print(e)
        
def main():
    
    p = Path("/Users/jonathan/0_jono_data")

    df = data_table(p)
    
    df = df.sort_values(by = 'acquisition_date', ascending = False)

    data = df.loc['2021-DEBORTOLI-CABERNET-MERLOT_HALO.D']['data']

    uv_data = retrieve_uv_data(data)
    

