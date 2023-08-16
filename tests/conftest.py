import pytest
import pandas as pd
from wine_analysis_hplc_uv.chemstation.chemstationprocessor import ChemstationProcessor
import numpy as np
from wine_analysis_hplc_uv import definitions
import duckdb as db

import os

db_path = definitions.DB_PATH
print(db_path)


@pytest.fixture
def corecon():
    assert isinstance(db_path, str)
    con = db.connect(db_path)
    return con


class DataPaths:
    def __init__(self):
        self.sampleset = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/agilent_D"
        self.fullset = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/agilent_D"


@pytest.fixture
def datapaths():
    return DataPaths()


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
def chemstationprocessor(datapaths):
    return ChemstationProcessor(datapaths.sampleset)
