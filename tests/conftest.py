import pytest
import pandas as pd
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.chemstation.chemstationprocessor import ChemstationProcessor
import numpy as np
import duckdb as db


@pytest.fixture
def con():
    return db.connect(definitions.DB_PATH)


@pytest.fixture
def ch_data_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/agilent_D"


@pytest.fixture
def ch_m_csv_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/test_ch_m_data.csv"


@pytest.fixture
def ch_d_csv_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/test_ch_d_data.csv"


@pytest.fixture
def verified_ch_d(ch_d_csv_path) -> None:
    return pd.read_csv(ch_d_csv_path).replace({np.nan: None})


@pytest.fixture
def verified_ch_m(ch_m_csv_path) -> None:
    return pd.read_csv(ch_m_csv_path).replace({np.nan: None})


@pytest.fixture
def chemstationprocessor(ch_data_path):
    return ChemstationProcessor(ch_data_path)
