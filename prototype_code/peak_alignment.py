import sys
import duckdb as db
sys.path.append('../../wine_analysis_hplc_uv')
from pathlib import Path
from prototype_code import db_methods
import pandas as pd
import numpy as np
from dtw import dtw
import matplotlib.pyplot as plt
from prototype_code import signal_data_treatment_methods as dt

def peak_alignment_pipe():
    con = db.connect('/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db')
    wavelength = '254'
    df = fetch_repres_spectra(con)

    df = extract_single_wavelength(df, wavelength)
    
#    df = df.set_index('name_ct', drop = True)

    print(type(df['254'].iloc[4]))
    
    # subtract baseline
    
    df = df.drop('spectrum', axis =1)

    y_df = extract_signal_y(df, wavelength=wavelength, key = 'name_ct')
    
    corr_df = y_df.corr().replace({1:np.nan})

    highest_corr_key = find_representative_sample(corr_df)

    y_df.plot()

    plt.show()
    peak_alignment(y_df, highest_corr_key)

def extract_signal_y(df : pd.DataFrame, wavelength : str, key : str) -> pd.DataFrame:

    try:
        df['signal_y'] = df.apply(lambda row : row['254']['254'].values, axis = 1)

        y_df = df[[key,'signal_y']].T.apply(pd.Series.explode).reset_index(drop = True)

        y_df.columns = y_df.loc[0,:]
        y_df = y_df.loc[1:,:]
    except Exception as e:
        print(e)


    return y_df

def fetch_repres_spectra(con : db. DuckDBPyConnection) -> None:
    with  con:
        query = """
        SELECT
            acq_date,
            new_id,
            vintage_ct,
            name_ct,
            varietal,
            super_table.hash_key
        FROM super_table
        WHERE
            super_table.hash_key LIKE '%ed669e74%'
            OR super_table.hash_key LIKE '%513fd979%'
            OR super_table.hash_key LIKE '%112f4287%'
            OR super_table.hash_key LIKE '%bf648dfb%'
            OR super_table.hash_key LIKE '%9b7abe4e%'
        """
    
        df = con.sql(query).df()
        df = db_methods.get_spectrums(df, con)
        
    return df

def extract_single_wavelength(single_wavelength_df : pd.DataFrame, wavelength : str) -> pd.DataFrame:

    def get_wavelength(spectrum_df : pd.DataFrame, wavelength) -> pd.DataFrame:
        spectrum_df = spectrum_df.set_index('mins')
        single_wavelength_df = spectrum_df[wavelength]
        single_wavelength_df = single_wavelength_df.to_frame().reset_index()

        return single_wavelength_df
    
    single_wavelength_df[wavelength] = pd.Series(single_wavelength_df.apply(lambda row : 
    get_wavelength(row['spectrum'], wavelength), axis = 1),index = single_wavelength_df.index)

    single_wavelength_df['signal_shape'] = single_wavelength_df.apply(lambda row : row[wavelength].shape, axis = 1)
    single_wavelength_df['signal_index'] = single_wavelength_df.apply(lambda row : row[wavelength].index, axis = 1)
    single_wavelength_df['signal_columns'] = single_wavelength_df.apply(lambda row : row[wavelength].columns, axis = 1)

    return single_wavelength_df

def find_representative_sample(corr_df = pd.DataFrame) -> str:

    corr_df['mean'] = corr_df.apply(np.mean)
    corr_df = corr_df.sort_values(by = 'mean', ascending=False)
    

    highest_corr_key = corr_df['mean'].idxmax()

    print(f"{corr_df['mean'].idxmax()} has the highest average correlation with {corr_df['mean'].max()}")

    return highest_corr_key

def peak_alignment(chromatograms, highest_corr_key):
    chromatograms = chromatograms.astype('float64')

    reference_chromatogram = chromatograms[highest_corr_key].to_numpy()
    chromatograms = pd.DataFrame(index=chromatograms.index)

    for column in chromatograms.columns:
        plt.plot(chromatograms[column], label=column)
    plt.legend()
    plt.show()

    for column in chromatograms.columns:
    
        chromatogram = chromatograms[column].to_numpy()

        # Calculate the DTW distance and path between the reference and current chromatogram
    
        alignment = dtw(reference_chromatogram, chromatogram, step_pattern='asymmetric', open_end=True, open_begin=True)

        # Align the current chromatogram to the reference chromatogram using the calculated path
        aligned_chromatogram = np.zeros_like(chromatogram)
        
        for i in range(len(alignment.index1)):
            ref_idx = alignment.index1[i]
            cur_idx = alignment.index2[i]
            aligned_chromatogram[cur_idx] = reference_chromatogram[ref_idx]

        # Add the aligned chromatogram to the aligned_chromatograms DataFrame
        chromatograms[column] = aligned_chromatogram

    # Plot the aligned chromatograms
    for column in chromatograms.columns:
        plt.plot(chromatograms[column], label=column)
    plt.legend()
    plt.show()

def main():
    peak_alignment_pipe()
    
if __name__ == '__main__':
    main()