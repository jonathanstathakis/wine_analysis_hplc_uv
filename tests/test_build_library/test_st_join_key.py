from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.core import st_ct_join
import pytest
import polars as pl
import duckdb as db
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def st(corecon):
    st_df = corecon.sql(
        f"SELECT samplecode, vintage, name FROM {definitions.CLEAN_ST_TBL_NAME} WHERE"
        " added_to_cellartracker='y'"
    ).df()
    assert not st_df.empty
    return st_df


@pytest.fixture
def ct(corecon):
    ct_df = corecon.sql(
        "SELECT VINTAGE, name, wine as ct_wine_name FROM"
        f" {definitions.CLEAN_CT_TBL_NAME}"
    ).df()
    assert not ct_df.empty
    return ct_df


@pytest.fixture
def formforeignkey(st, ct):
    formforeignkey = st_ct_join.FormForeignKeySTCT(st, ct)
    return formforeignkey


def test_form_join_df(formforeignkey):
    st_ct_df = formforeignkey.get_fuzzy_join_df()
    st_ct_df = pl.from_pandas(st_ct_df)

    with pl.Config(fmt_str_lengths=50, set_tbl_cols=10, set_tbl_rows=200):
        logger.info(f"\n{st_ct_df.sort(by='join_key_similarity')}")


def test_add_foreign_key(formforeignkey, corecon):
    st_df = corecon.sql("SELECT * FROM c_sample_tracker").df()
    logging.info(st_df.shape)

    formforeignkey.st_with_foreign_key(corecon)

    new_st_df = corecon.sql("SELECT * FROM st_temp_join1").df()
    logging.info(new_st_df.shape)

    # check if only 1 column added and same rows as st_df
    assert new_st_df.shape == tuple([st_df.shape[0] + 1, st_df.shape[1]])

    # check if any nulls
    for col in st_df.drop("wine", axis=1).columns:
        assert new_st_df[col].isna().sum() == 0
