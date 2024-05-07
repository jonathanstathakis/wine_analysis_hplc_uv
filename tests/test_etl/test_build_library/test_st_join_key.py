from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.core import st_ct_join
import pytest
import polars as pl
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def st(corecon):
    st_df = corecon.sql(
        "SELECT * FROM c_sample_tracker WHERE" " added_to_cellartracker='y'"
    ).df()
    assert not st_df.empty
    return st_df


@pytest.fixture
def ct(corecon):
    ct_df = corecon.sql("SELECT * FROM" f" {definitions.CLEAN_CT_TBL_NAME}").df()
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
    formforeignkey.st_with_foreign_key(corecon)
