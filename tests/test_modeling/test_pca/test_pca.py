import pytest
import logging
import duckdb as db
from wine_analysis_hplc_uv.modeling import pca
from wine_analysis_hplc_uv.db_methods import get_data

import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def wine_data(corecon):
    get_data.get_wine_data(
        corecon, samplecode=("124", "130", "125", "133", "174"), wavelength=(450,)
    )
    df = corecon.sql("SELECT * FROM wine_data").df()
    return df


def test_get_wine_data(wine_data):
    # check if empty and if any nulls. no nulls expected
    assert not wine_data.empty
    assert wine_data.isna().sum().sum() == 0


# wine data columns:
# Index(['detection', 'samplecode', 'wine', 'color', 'varietal', 'id', 'mins',
# 'wavelength', 'value'],
def test_pivot_wine_data(wine_data):
    # test pivoting wine data
    p_wine_data = pca.pivot_wine_pddf(wine_data)

    assert not p_wine_data.empty
