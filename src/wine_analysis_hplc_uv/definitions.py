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

TEST_PARQ_PATH = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/processing_test_set/cupshz_testset.pq"

# path to the y-axis processed (not baseline corrected) file
PRO_PARQ_PATH = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/processing_test_set/y_pro_cuprac_shzset.pq"
