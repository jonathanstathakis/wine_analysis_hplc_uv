"""
~~rule: signal dataframes are always structured index | mins | signal~~
rule: dataframes with a combination of signal and metadata will always have the sample 
name as the index.
rule: use dictionaries to handle collections of dataframes.
rule: ditch time.

1. interpolate time axis, then just store 1 time array in a df. reduces dimensionality
by 1.

2023-08-20 18:37:26: Revitalizing the pipe. Ideally we're gna convert it to a 
multiindexed approach of (samplecode, wine, signal).
2023-08-20 18:39:20: TBH I should create a mock df in the format the pipe is expecting
in order to test the pipe before and after structure format conversion.
2023-08-20 18:44:33: since I have a function to form the old-style data structure
format, I can use them, but that will require reforming the super table, at least in
some form.
2023-08-20 18:46:47: because the hash is different, I wont be able to form the sample
dataset that the pipe was originally formed on.
2023-08-21 14:10:45: because db_methods.get_spectra has been deleted, and I cant be
bothered trying to revert to an undeleted state, I'll just form a mock structure from
the current multiindexed structure.
2023-08-21 14:55:56: the baseline subraction module actually acts on a series of 
dataframes, not a dict. minimal difference..

TODO:
- [x] test pipe with mock df
- [ ] convert pipeline to multiindexed data structure
    - [ ] get rid of pickling approaches


"""

import os
import pickle
import shutil
import sys

import duckdb as db
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
from typing import List, Union

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.plot_methods import plotly_plot_methods
from wine_analysis_hplc_uv.scripts.core_scripts import (
    signal_data_treatment_methods as dt,
)
from wine_analysis_hplc_uv.signal_processing import signal_alignment_methods as sa
from wine_analysis_hplc_uv.signal_processing import signal_data_treatment_methods as sdt

# create your figure and get the figure object returned


def pickle_pipe_check(
    db_path: str,
    wavelength: Union[str, List[str]] = None,
    display_in_st: bool = False,
    pickle_dir_name: str = None,
):
    peak_alignment_pipe_pickle_dir_name = "peak_alignment_pipe_pickle_jar"
    # test if pickle dir exists, if not, create it.
    if not os.path.isdir(f"{peak_alignment_pipe_pickle_dir_name}"):
        create_pipe_pickle = input(
            "no peak alignment pipe pickle dir detected, create now? (y/n): "
        )
        if create_pipe_pickle == "y":
            os.mkdir(f"{peak_alignment_pipe_pickle_dir_name}")
            print(f"pickle jar created at {peak_alignment_pipe_pickle_dir_name}")
        elif create_pipe_pickle == "n":
            peak_alignment_pipe_pickle_dir_name = None
            df = peak_alignment_pipe(
                db_path,
                wavelength,
                pickle_path_prefix=peak_alignment_pipe_pickle_dir_name,
            )
        else:
            print("bad input, try again.")

    if os.path.isdir(f"{peak_alignment_pipe_pickle_dir_name}"):
        use_prev_pickle = input("use previous peak alignment pipe pickle? (y/n): ")
        if use_prev_pickle == "y":
            df = peak_alignment_pipe(
                db_path, wavelength, peak_alignment_pipe_pickle_dir_name
            )
        elif use_prev_pickle == "n":
            shutil.rmtree(peak_alignment_pipe_pickle_dir_name)
            os.mkdir(peak_alignment_pipe_pickle_dir_name)
            df = peak_alignment_pipe(
                db_path,
                wavelength,
                pickle_path_prefix=peak_alignment_pipe_pickle_dir_name,
            )
        else:
            print("bad input try again")


def rw_pipe_pickle(series: pd.Series, pickle_dir_path: str = None):
    """
    read and write a series of dataframes to store parts of the peak alignment pipe.
    """
    if pickle_dir_path == None:
        return

    filepath = os.path.join(pickle_dir_path, f"{series.name}.pk")

    if not os.path.isfile(filepath):
        print(f"{filepath} does not exist, creating pickle now")

        with open(filepath, "wb") as f:
            pickle.dump(df, f)
    else:
        print(f"reading {filepath}")
        with open(filepath, "rb") as f:
            df = pickle.load(f)
    return df


def get_unaligned_data(
    db_path: str,
    pickle_path_prefix: "str" = None,
    wavelength: Union[str, List[str]] = None,
):
    con = db.connect(db_path)
    raw_signal_col_name = f"raw {wavelength}"
    df = get_library(con, wavelength, raw_signal_col_name)
    return df


import pandera as pa
from pandera.typing import DataFrame, Series


class SampleSignalSchema(pa.DataFrameModel):
    mins: Series[float]
    value: Series[float]


class PeakAlignmentPipeSchema(pa.DataFrameModel):
    raw_df: Series[DataFrame[SampleSignalSchema]]


def peak_alignment_pipe(df: DataFrame[PeakAlignmentPipeSchema]):
    """
    A pipe to align a supplied library of chromatograms.
    """
    # get the library and 254 nm signal

    st.subheader("Group Contents")
    st.write(df)

    # get raw matrices
    st.header("raw signal")

    signal_df_series = (
        df["raw_df"]
        .pipe(peak_alignment_st_output)
        .pipe(
            sa.baseline_subtraction
        )  # subtract baseline. If baseline not subtracted, alignment WILL NOT work.
        .pipe(peak_alignment_st_output)
        .pipe(sdt.normalize_library_absorbance)
        .pipe(peak_alignment_st_output)
        .pipe(sa.interpolate_chromatogram_times)
        .pipe(peak_alignment_st_output)
    )
    # calculate correlations between chromatograms as pearson's r, identify sample with highest average correlation, store key as most represntative sample for downstream peak alignment.
    highest_corr_key = (
        signal_df_series.pipe(sample_name_signal_df_builder)
        .corr()
        .pipe(find_representative_sample)
    )
    (
        signal_df_series.pipe(sa.peak_alignment, highest_corr_key).pipe(
            peak_alignment_st_output
        )
    )

    # # # align the library time axis with dtw
    # peak_aligned_series_name = f'aligned_{wavelength}'
    # df[peak_aligned_series_name] = sa.peak_alignment(df[time_interpolated_chromatogram_name], highest_corr_key)

    return df


def get_library(
    con: db.DuckDBPyConnection, wavelength: str, signal_col_name: str
) -> pd.DataFrame:
    # get the selected runs to build the library
    df = fetch_sample_dataframes_with_spectra(con)
    df = df.set_index("name_ct", drop=True)

    # select the 254nm wavelength column across the library

    df[signal_col_name] = dt.subset_spectra(df["spectra"], wavelength)

    # 2023-08-21 14:53:06 at this point its a long form df with [name_ct, mins, value]
    df = df.drop("spectra", axis=1)

    return df


def fetch_sample_dataframes_with_spectra(con: db.DuckDBPyConnection) -> None:
    with con:
        query = """
        SELECT
            acq_date,
            join_samplecode,
            vintage_ct,
            name_ct,
            varietal,
            hash_key
        FROM super_table
        WHERE
            super_table.hash_key LIKE '%ed669e74%'
            OR super_table.hash_key LIKE '%513fd979%'
            OR super_table.hash_key LIKE '%112f4287%'
            OR super_table.hash_key LIKE '%bf648dfb%'
            --OR super_table.hash_key LIKE '%9b7abe4e%'
        """

        df = con.sql(query).df()
        df = db_methods.get_spectra(df, con)

    return df


def sample_name_signal_df_builder(df_series: pd.Series):
    # extract the sample names as column names, y_axis column as column values.
    sample_name_signal_df = pd.DataFrame(columns=df_series.index)

    for idx, row in df_series.items():
        sample_name_signal_df[idx] = row.iloc[:, 1]

    return sample_name_signal_df


def find_representative_sample(corr_df=pd.DataFrame) -> str:
    corr_df = corr_df.replace({1: np.nan})
    corr_df["mean"] = corr_df.apply(np.mean)
    corr_df = corr_df.sort_values(by="mean", ascending=False)
    highest_corr_key = corr_df["mean"].idxmax()

    st.header("spectrum correlation matrix")
    st.write(corr_df)
    st.subheader("average highest correlation value")
    st.write(corr_df["mean"])
    st.write(
        f"{corr_df['mean'].idxmax()} has the highest average correlation with"
        f" {corr_df['mean'].max()}\n"
    )

    return highest_corr_key


def peak_alignment_st_output(series: pd.Series) -> None:
    """
    Display the intermediate and final results of the the pipeline. As each stage of the pipeline is stored in the df as a column idx : wine, column : dfs, can iterate through the columns, using the col naems as section headers.
    """
    st.subheader(f"{series.name}")

    x_axis_name = list(series.iloc[0].columns)[0]
    y_axis_name = list(series.iloc[0].columns)[1]

    fig = plotly_plot_methods.plot_signal_in_series(series, x_axis_name, y_axis_name)

    st.plotly_chart(fig)

    return series


def get_mock_df():
    df = pd.DataFrame(dict(mins=[1, 2, 3, 4, 5], signal=[0, 10, 100, 10, 0]))
    return dict(df1=df)


def main():
    pickle_filepath = "alignment_df_pickle.pk1"
    db_path = definitions.DB_PATH
    wavelength = "254"
    display_in_st = True

    pickle_pipe_check(db_path, wavelength, pickle_filepath)


if __name__ == "__main__":
    main()
