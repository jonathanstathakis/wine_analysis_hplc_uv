import pandas as pd

import numpy as np

import rainbow as rb

from pathlib import Path

from sklearn.preprocessing import MinMaxScaler

from pybaselines import Baseline

from scipy.signal import find_peaks

def get_uv_data():

    root_dir_path = Path('/Users/jonathan/0_jono_data')

    uv_data = list(root_dir_path.glob('**/*.UV'))

    sample_uv_data = uv_data[0:2]

    return sample_uv_data


def main():

    # id the target files as a list
    sample_uv_paths = ['/Users/jonathan/0_jono_data/2023-02-15_COFFEE_COLUMN_CHECK.D/DAD1.UV', '/Users/jonathan/0_jono_data/5test_sequence/2023-02-22_STONEY-RISE-PN_02-21.D/DAD1.UV']

    # form a df with the list of files as the first column
    uv_dataframe = pd.DataFrame(sample_uv_paths, columns = ['file_path'], index = pd.Index([Path(path).parent.name for path in sample_uv_paths], name = 'run'))

    uv_dataframe['uv_object'] = uv_dataframe.apply(lambda row : rb.agilent.chemstation.parse_uv(row['file_path']), axis = 1)

    # form the spectrum dataframes.

    # note to self: always instantiate columns and indexes as type pd.Index() so you can control their behavior, name them etc. in the constructor.
    
    uv_dataframe['spectrum'] = uv_dataframe.apply( lambda row : pd.DataFrame(row['uv_object'].data, columns = pd.Index(row['uv_object'].ylabels, name = 'nm'), index = pd.Index(row['uv_object'].xlabels, name = 'mins')), axis = 1)

    # scale the uv_data

    scaler = MinMaxScaler()
    
    uv_dataframe['scaled_spectrum'] = uv_dataframe['spectrum'].apply(lambda col : pd.DataFrame(scaler.fit_transform(col), columns = col.columns, index = col.index))

    # calculate the baselines

    # fit the baseline obj for each nm column in each scaled_uv_data row/col.

    # first form the baseline fitting obj for each nm.
    
    uv_dataframe['baseline_obj'] = uv_dataframe['scaled_spectrum'].apply(lambda col_spectrum : Baseline(col_spectrum.index))

    uv_dataframe['spectrum_baseline'] = uv_dataframe.apply(lambda row : row['scaled_spectrum'].apply(lambda spectrum_col : row['baseline_obj'].iasls(spectrum_col)[0]), axis = 1)

    # baseline subtraction. The baselines exist in a df with the same index as the spectrum so it should be as straight forward as get the row, get the rows spectrum and rows baselines, and subtract one from the other.
    
    uv_dataframe['baseline_corrected_scaled_spectrum'] = uv_dataframe.apply(lambda row : row['scaled_spectrum'] - row['spectrum_baseline'], axis = 1)

    a = uv_dataframe['baseline_corrected_scaled_spectrum'][0]

    # av baseline grad

    uv_dataframe['av_baseline_grad'] = uv_dataframe.apply(lambda row : pd.DataFrame(row['spectrum_baseline'].apply(lambda baseline_col : np.mean(np.gradient(baseline_col))), columns = ['av_baseline_gradient']), axis = 1)

    # peaks

    # for each spectrum column find x and y of peaks. Return as a series with x as index, named '{nm_col.name}_peaks'.

    def peak_getter(nm_col):
        peak_idx, peak_y = find_peaks(height = 0.05, x = nm_col.values)
        peak_y = peak_y['peak_heights']
        peak_x = nm_col.index[peak_idx].values

        series = pd.Series(peak_y, index = pd.Index(peak_x, name = 'mins'), name = f"{nm_col.name}_peaks")
        
        return series

    # Apply peak_getter to each column of the spectrum, returning a sparse dataframe with total chromatogram mins as index and values for each nm_column for each peak maxima. These dataframes are then indexed and returned as a series as the column 'peaks_per_nm'. Not sure whether the sparseness will have a negative effect.

    uv_dataframe['peaks_per_nm'] = uv_dataframe.apply(lambda row : row['baseline_corrected_scaled_spectrum'].apply( lambda col : peak_getter(col)), axis = 1)

    # calculate the average peak height. Guess you could use the same structure as the average baseline gradient.
    
    #uv_dataframe['av_baseline_grad'] = uv_dataframe.apply(lambda row : pd.DataFrame(row['spectrum_baseline'].apply(lambda baseline_col : np.mean(np.gradient(baseline_col))), columns = ['av_baseline_gradient']), axis = 1)

    #uv_dataframe['av_peak_height_per_nm'] 
    
    peak_avs = uv_dataframe.apply(lambda row: row['peaks_per_nm'].apply(lambda col: np.mean(col)), axis = 1, result_type = 'reduce')

    # The current algorithm is returning a dataframe whose rows correspond tot he run, and each column is a nm. almost perfect, but im expecting to be.. expecting again a 

    print(peak_avs)

main()
    