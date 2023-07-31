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
    join_df = formforeignkey.get_fuzzy_join_df()

    logger.info(join_df.columns)

    # create temp st table with join_key_col

    st_temp = corecon.sql(
        """--sql
                      CREATE TEMPORARY TABLE st_temp
                      AS
                      SELECT * FROM c_sample_tracker;
                      ALTER TABLE
                      st_temp
                      ADD COLUMN
                      join_key VARCHAR;
                      UPDATE st_temp
                      SET join_key = concat(st_temp.vintage,' ',st_temp.name);
                      SELECT * FROM st_temp LIMIT 5;
                      """
    ).pl()

    logger.info(st_temp.describe())

    # sql_st_with_fkey = corecon.sql("""--sql
    #                         CREATE TEMP table st_wfkey
    #                         AS
    #                         SELECT st.detection, st.sampler, st.samplecode, st.vintage, st.name, st.open_date, st.sampled_date, st.added_to_cellartracker, st.notes, st.size, join_df.ct_wine_name
    #                         FROM c_sample_tracker st
    #                         JOIN join_df
    #                         ON (st.vintage || ' ' || st.name) = (join_df.vintage_st || ' ' || join_df.name_st)
    #                         """).pl()

    # logger.info(sql_st_with_fkey.describe())

    # logger.info(formforeignkey.st_with_foreign_key())
