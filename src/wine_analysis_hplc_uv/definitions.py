import os
from enum import StrEnum
from pathlib import Path

# '/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# pbl dir

PBL = str(Path(ROOT_DIR) / "etl/post_build_library")

DB_PATH: str = os.environ["DB_PATH"]

LIB_DIR = "/Users/jonathan/uni/0_jono_data/mres_data_library/"


# the names of the raw tables, the data prior to cleaning
class Raw_tbls(StrEnum):
    CH_META = "chemstation_metadata"
    CH_DATA = "chromatogram_spectra"
    ST = "sample_tracker"
    CT = "cellar_tracker"


# the names of the clean tables - the names of the raw tables with a "c_" prefixed
class Clean_tbls(StrEnum):
    CH_META = "c_" + Raw_tbls.CH_META
    ST = "c_" + Raw_tbls.ST
    CT = "c_" + Raw_tbls.CT


# the login information required to access the Google Sheets API
class GoogleSheetsAPIInfo(StrEnum):
    SHEET_TITLE = os.environ["SAMPLE_TRACKER_SHEET_TITLE"]
    GKEY = os.environ["SAMPLE_TRACKER_KEY"]
    USERNAME = os.environ["CELLAR_TRACKER_UN"]
    PW = os.environ["CELLAR_TRACKER_PW"]


SUPER_TBL_NAME = "super_tbl"
TEST_DB_PATH = os.path.join(os.getcwd(), "tests", "test.db")
TEST_GKEY = os.environ.get("TEST_SAMPLE_TRACKER_KEY")

ID_COLNAME = "id"

TEST_WINE_NAMES = [
    "2021 babo chianti",
    "2020 boutinot uva non grata",
    "2021 matias riccitelli malbec hey malbec!",
    "2018 crawford river cabernets",
    "2021 john duval wines shiraz concilio",
]

BAD_CUPRAC_SAMPLES = ["128", "161", "163", "164", "165", "ca0101", "ca0301"]

# the unprocesssed cupshz dataset

RAW_PARQ_PATH = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/processing_test_set/cupshz_testset_raw.pq"

XPRO_DOWNSAMPLED_PARQ_PATH = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/processing_test_set/cupshz_testset_x.pq"

# path to the y-axis processed (not baseline corrected) file
XPRO_YPRO_DOWNSAMPLED_PARQ_PATH = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/processing_test_set/y_pro_cuprac_shzset_xy.pq"

# red wine cuprac 450nm processed data. Time standardized, cleaned of dud samples, baseline corrected and DTW aligned.

RW_CUP_450_PROCESSED = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/rw_cup_450_processed.parquet"

# tidy format dset of raw detected samples for MCR-ALS
RAW3DDSET = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/tidy_3d_dset_raw.parquet"

# use ids to exclude samples rather than codes
EXCLUDEIDS = {
    # aborted run, other 72 is full
    "72": "6d8a370a-9f40-460d-acba-99fd4c287ad8",
    # recorded at double sampling rate of everything else resulting in twice as many data points as everything else
    "98": "6bf0e36f-819a-4303-9386-76d206ce3bfb",
}
