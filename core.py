"""
The main file of the wine_analysis_hplc_uv thesis project. Will act as the overarching pipeline to get to final results.
"""

from prototype_code import build_library
from prototype_code import peak_alignment

def core():
    """
    Project main file driver function. A pipe to go from start to finish.
    """
    # Phase 1: collect and preprocess data

    build_library.build_library(db_path = 'wine_auth_db.db', data_lib_path = "/Users/jonathan/0_jono_data")

    # Phase 2: process data

    peak_alignment.peak_alignment_pipe(db_path = '/Users/jonathan/wine_analysis_hplc_uv/prototype_code/wine_auth_db.db')

    # Phase 3: Data Analysis

    # Phase 4: Model Building

    # Phase 5: Results Aggregation and Reporting

def main():
    core()
 
if __name__ == "__main__":
    main()