"""
The main file of the wine_analysis_hplc_uv thesis project. Will act as the overarching pipeline to get to final results.
"""
from devtools import project_settings
import os
import core
from signal_processing.peak_alignment import peak_alignment_pipe
from core import build_library as bl

def core():
    """
    Project main file driver function. A pipe to go from start to finish.
    """
    # Phase 1: collect and preprocess data

    bl.build_library(db_path = 'wine_auth_db.db', data_lib_path = "/Users/jonathan/0_jono_data")

    # Phase 2: process data

    peak_alignment_pipe.peak_alignment_pipe(db_path = '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db')

    # Phase 3: Data Analysis

    # Phase 4: Model Building

    # Phase 5: Results Aggregation and Reporting

def main():
    core()
 
if __name__ == "__main__":
    main()