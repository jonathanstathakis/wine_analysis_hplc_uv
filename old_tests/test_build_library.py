"""
TODO:
- [ ] add automation
"""

import pytest

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.core import build_library
import os


@pytest.fixture
def get_test_db_path():
    dirpath = os.path.dirname(os.path.abspath(__file__))
    db_filename = "test_build_library.db"
    fullpath = os.path.join(dirpath, db_filename)
    return fullpath


@pytest.fixture
def get_datalibpath():
    return definitions.LIB_DIR


def test_build_library(get_test_db_path, get_datalibpath):
    build_library.build_db_library(
        data_lib_path=get_datalibpath, db_path=get_test_db_path
    )
