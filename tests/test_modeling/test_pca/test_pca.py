import pytest
import logging
import duckdb as db
from wine_analysis_hplc_uv import definitions


@pytest.fixture
def get_dataset():
    con = db.connect(definitions.DB_PATH)

    super_tbl_rel = con.sql("SELECT * FROM super_tbl").show()
    print(super_tbl_rel)


def test_pca(get_dataset):
    a = get_dataset
    print(a)
