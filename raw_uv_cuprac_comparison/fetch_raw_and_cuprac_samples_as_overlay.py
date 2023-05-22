"""
A module for generating a report for Andrew to send to AWRI.

It will initially consist of a pipe to fetch selected sample spectrum chromatograms from the db.
"""
import os
from typing import List

import duckdb as db
import pandas as pd
import streamlit as st
from scplot.plotly_plot_methods import plot_signal_in_series
from wine_analysis_hplc_uv import 

def get_signals(filepath: str) -> dict:


def main():
    db_filepath = os.environ.get("WINE_AUTH_DB_PATH")
    tbl_name = "super_table"

    st.set_page_config(layout="wide")
    st.write(df)

    return None


if __name__ == "__main__":
    main()
