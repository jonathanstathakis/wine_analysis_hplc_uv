from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.etl.build_library import st_ct_join
import pytest
import polars as pl
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def st(con):
    st_df = con.sql(
        "SELECT * FROM c_sample_tracker WHERE" " added_to_cellartracker='y'"
    ).df()
    assert not st_df.empty
    return st_df


@pytest.fixture
def ct(con):
    ct_df = con.sql("SELECT * FROM" f" {definitions.Clean_tbls.CT}").df()
    assert not ct_df.empty
    return ct_df


@pytest.fixture
def ffk(st, ct):
    ffk = st_ct_join.FormForeignKeySTCT(st, ct)
    return ffk


@pytest.mark.skip(reason="is currently running forever. Needs to be fixed")
def test_form_join_df(ffk) -> None:
    """
    FIXME: test is currently not working, is instead running forever. possible critical error
    """
    st_ct: pl.DataFrame = pl.from_pandas(ffk._get_fuzzy_join_df()).sort(
        by="join_key_similarity"
    )

    with pl.Config(fmt_str_lengths=50, set_tbl_cols=10, set_tbl_rows=200):
        logger.info(f"\n{st_ct}")


@pytest.mark.xfail(
    reason="null values present in output table due to either wines missing from cellar tracker, or the similarity metric is failing. See function docstring for remedy plan"
)
def test_add_foreign_key(ffk, con):
    """
    Test whether we are able to add the ct 'wine_name' foreign key to sample tracker
    """
    ffk.write_st_with_foreign_key(con)
