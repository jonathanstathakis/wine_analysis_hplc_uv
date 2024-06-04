"""
Produce a pairwise euclidean distance matrix of sample sc matrices.

1. Get the samples and their sc matrices as a dataframe with 1 column of nested dataframes (the sc matrices). On the first run pickles the dataframe, then loads from the pickle for subsequent runs.
2. Construct the pairwise-distance matrix.
3.
"""

import os
import pickle
import duckdb as db
import pandas as pd
import streamlit as st

from wine_analysis_hplc_uv.etl.build_library.db_methods import db_methods
from wine_analysis_hplc_uv.old_signal_processing.peak_alignment import (
    observing_spectra_shape_variation,
)
from wine_analysis_hplc_uv.old_signal_processing import signal_alignment_methods as sa
from wine_analysis_hplc_uv.old_signal_processing import (
    signal_data_treatment_methods as dt,
)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


def peak_alignment_spectrum_chromatogram():
    # get a dataframe consisting of sample metadata and a column of sc matrices as nested dataframes.
    df = load_spectrum_chromatograms()
    df = df.drop("join_samplecode", axis=1)
    df = df.set_index("wine")

    df = observing_spectra_shape_variation.observe_sample_size_mismatch(df)
    df["normalized_matrix"] = dt.normalize_library_absorbance(df["reshaped_matrix"])

    series = df["normalized_matrix"]

    # subsetting series while testing code
    series = series[:5]

    for idx, tab in enumerate(st.tabs(list(series.keys()))):
        with tab:
            st.table(series[idx].describe())

    try:
        sim_df = sa.calculate_distance_matrix(series)
        st.table(sim_df)
    except Exception as e:
        print(e)


def query_unique_wines_spectra_to_df(con: db.DuckDBPyConnection):
    raise NotImplementedError(
        "modifications to library has rendered this function unusable"
    )
    print("starting")

    with con:
        query = """
            SELECT ANY_VALUE(join_samplecode) AS join_samplecode, CONCAT(vintage_ct, ' ', name_ct) AS wine, ANY_VALUE(hash_key) AS hash_key, ANY_VALUE(path) AS path
            FROM super_table
            GROUP BY wine;
        """
        print("getting metadata_df")
        df = con.sql(query).df()
        print("getting spectra")

        df = db_methods.get_sc_df(df, con)

    return df


def write_unique_id_spectra_df(df: pd.DataFrame, filepath: str):
    print("writing pickle")
    with open(filepath, "wb") as file:
        pickle.dump(df, file)
    return None


def read_unique_id_spectra_pickle(filepath: str):
    print("reading pickle")
    with open(filepath, "rb") as file:
        df = pickle.load(file)
    return df


def load_spectrum_chromatograms():
    table_name = "unique_join_samplecode_spectra"
    filepath = table_name + ".pk1"

    # Check if the pickle file exists
    if not os.path.isfile(filepath):
        print("establishing conn. with db")
        db_path = os.environ["WINE_AUTH_DB_PATH"]
        con = db.connect(db_path)
        df = query_unique_wines_spectra_to_df(con)
        write_unique_id_spectra_df(df, filepath)

    else:
        df = read_unique_id_spectra_pickle(filepath)

    return df


def main():
    peak_alignment_spectrum_chromatogram()


if __name__ == "__main__":
    main()
