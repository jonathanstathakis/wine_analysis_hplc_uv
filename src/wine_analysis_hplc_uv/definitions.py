import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.environ.get("DB_PATH")

LIB_DIR = "/Users/jonathan/uni/0_jono_data/mres_data_library/"

CH_META_TBL_NAME = "chemstation_metadata"
CH_DATA_TBL_NAME = "chromatogram_spectra"
ST_TBL_NAME = "sample_tracker"
CT_TBL_NAME = "cellar_tracker"

CLEAN_CH_META_TBL_NAME = "c_" + CH_META_TBL_NAME
CLEAN_ST_TBL_NAME = "c_" + ST_TBL_NAME
CLEAN_CT_TBL_NAME = "c_" + CT_TBL_NAME

SUPER_TBL_NAME = "super_tbl"

TEST_DB_PATH = os.path.join(os.getcwd(), "tests", "test.db")

TEST_SHEETS_KEY = os.environ.get("TEST_SAMPLE_TRACKER_KEY")

ID_COLNAME = "id"

TEST_WINE_NAMES = [
    "2021 babo chianti",
    "2020 boutinot uva non grata",
    "2021 matias riccitelli malbec hey malbec!",
    "2018 crawford river cabernets",
    "2021 john duval wines shiraz concilio",
]

BAD_CUPRAC_SAMPLES = ["128", "161", "163", "164", "165", "ca0101", "ca0301"]

# red wine cuprac 450nm processed data. Time standardized, cleaned of dud samples, baseline corrected and DTW aligned.

RW_CUP_450_PROCESSED = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/rw_cup_450_processed.parquet"

# tidy format dset of raw detected samples for MCR-ALS
RAW3DDSET = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/tidy_3d_dset_raw.parquet"


# list of raw samples identified as outliers, to be excluded from downstream analysis

RAWSAMPLEOUTLIERCODES = "98"

# a dict of sample ids identified as outliers - kept as a dict to make the id relatable.
# To use, call the `.values()` method then convert to a list with `list()`.

RAWSAMPLEOUTLIERIDS = {
    # this repetition of 72 is an aborted run
    "72": "6d8a370a-9f40-460d-acba-99fd4c287ad8",
    # observed at 1.1T as opposed to 2.5T like all other samples. To use will need to be resampled.
    "98": "6bf0e36f-819a-4303-9386-76d206ce3bfb",
}
