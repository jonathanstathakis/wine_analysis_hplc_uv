import pytest
import logging
import duckdb as db
from wine_analysis_hplc_uv import db_methods, definitions
from wine_analysis_hplc_uv.modeling import pca

import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def wine_data(corecon):
    wine_data = pca.get_wine_data(corecon)
    return wine_data


def test_get_wine_data(wine_data):
    # check if empty and if any nulls. no nulls expected
    assert not wine_data.empty
    assert wine_data.isna().sum().sum() == 0


# wine data columns:
# Index(['detection', 'samplecode', 'wine', 'color', 'varietal', 'id', 'mins',
# 'wavelength', 'value'],
def test_pivot_wine_data(wine_data):
    # test pivoting wine data
    p_wine_data = pca.pivot_wine_data(wine_data)
    assert not p_wine_data.empty
