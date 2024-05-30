"""
Global level test fixtures
"""

import os
from pathlib import Path
from enum import StrEnum
import pytest
import pandas as pd
from wine_analysis_hplc_uv.etl.build_library.chemstation.chemstationprocessor import (
    ChemstationProcessor,
)
import numpy as np
import duckdb as db


@pytest.fixture(scope="session")
def test_db_path():
    path = str(Path(__file__).parent.parent.parent / "test.db")

    return path


# the expected number of samples. Use to verify table size (rows)
NUM_SAMPLES = 175


@pytest.fixture(scope="module")
def testcon(test_db_path: str):
    """
    Return a duckdb connection object initialised with the DB_PATH constant
    """
    assert isinstance(test_db_path, str)
    con = db.connect(test_db_path)
    return con


TEST_DATA_DIRPATH: str = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/data"


class DataForTests(StrEnum):
    """
    Storage class for test data filepaths
    """

    SAMPLESET = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/data/agilent_D"
    FULLSET = "Nothing"
    VERIFIED_CH_M = str(Path(TEST_DATA_DIRPATH, "test_ch_m_data.csv"))


@pytest.fixture(scope="session")
def datapaths():
    """
    Return the StrEnum DataForTests
    """
    return DataForTests


@pytest.fixture
def ch_m_csv_path(scope="session"):
    """
    Return the filepath for the test chemstation metadata file
    """
    return str(Path(TEST_DATA_DIRPATH, "test_ch_m_data.csv"))


@pytest.fixture(scope="session")
def ch_d_csv_path():
    """
    Return the filepath for the test chromato-spectral data file
    """
    return str(Path(TEST_DATA_DIRPATH, "test_ch_d_data.csv"))


@pytest.fixture(scope="module")
def verified_ch_d(ch_d_csv_path) -> pd.DataFrame:
    """
    Return a Pandas DataFrame of test chromato-spectral data
    """
    return pd.read_csv(ch_d_csv_path).replace({np.nan: None})


@pytest.fixture(scope="module")
def verified_ch_m() -> pd.DataFrame:
    """
    Return a Pandas DataFrame of test chemstation metadata
    """
    return pd.read_csv(DataForTests.VERIFIED_CH_M).replace({np.nan: None})


@pytest.fixture(scope="module")
def chemstationprocessor(datapaths: DataForTests):
    """
    Return an instance of ChemstationProcessor intialised on the sampleset test data
    """
    return ChemstationProcessor(datapaths.SAMPLESET)


class BLTestFilePaths(StrEnum):
    """
    filepaths to database paths relevent to testing `build_library`
    """

    SAMPLESET = str(DataForTests.SAMPLESET)
    NEW_DB_PATH = str((Path(TEST_DATA_DIRPATH) / "temp_bl_output").with_suffix(".db"))
    COMPARISON = str(
        (Path(TEST_DATA_DIRPATH) / "test_bl_comparison").with_suffix(".db")
    )


@pytest.fixture(scope="module")
def bl_test_filepaths():
    return BLTestFilePaths


@pytest.fixture
def gsheets_key(scope="module"):
    return os.environ["TEST_SAMPLE_TRACKER_KEY"]
