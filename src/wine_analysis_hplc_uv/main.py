#!/usr/bin/env python3
"""
The main file of the wine_analysis_hplc_uv thesis project. Will act
as the overarching pipeline to get to final results.
"""
import os

from wine_analysis_hplc_uv.core import build_library
from wine_analysis_hplc_uv.devtools import project_settings
from wine_analysis_hplc_uv.signal_processing.peak_alignment import peak_alignment_pipe


def core(data_lib_path: str) -> None:
    """
    Project main file driver function. A pipe to go from start to finish.
    """
    # Phase 1: collect and preprocess data
    build_library.build_db_library(data_lib_path)

    # Phase 2: process data

    # peak_alignment_pipe.peak_alignment_pipe(db_path = \
    # '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db')

    # Phase 3: Data Analysis

    # Phase 4: Model Building

    # Phase 5: Results Aggregation and Reporting


def main():
    data_lib_path = (
        "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/data/cuprac_data"
    )
    core(data_lib_path)


if __name__ == "__main__":
    main()