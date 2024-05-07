from wine_analysis_hplc_uv.etl import generic
from tests.test_etl.test_post_build_library import gen_sample_test_data
import duckdb as db
import polars as pl


def get_stg(
    con: db.DuckDBPyConnection,
    sm_tblname: str = "sample_metadata",
    cs_tblname: str = "chromatogram_spectra_long",
    join_key: str = "id",
    sm_sample_tblname: str = "sm_sample",
    cs_sample_tblname: str = "cs_sample",
    n: int = 5,
) -> gen_sample_test_data.SampleTableGenerator:
    """
    Generate the sample tables and return the table names
    """
    stg = gen_sample_test_data.SampleTableGenerator(
        con=con,
        n=n,
        sample_metadata_tblname=sm_tblname,
        cs_tblname=cs_tblname,
        join_key=join_key,
        sm_sample_tblname=sm_sample_tblname,
        cs_sample_tblname=cs_sample_tblname,
    )

    return stg


def test_sample_table_generator(
    con: db.DuckDBPyConnection,
):
    try:
        stg = get_stg(con=con)
        stg.gen_samples()
        # test if they exist, if they match the expected schema, and number of distinct ids.

        # test if the new tables exist as temp tables

        sm_sample_tblname = stg.sm_sample_tblname
        cs_sample_tblname = stg.cs_sample_tblname
        join_key = stg.join_key
        n = stg.n

        tbls = [sm_sample_tblname, cs_sample_tblname]

        for tbl in tbls:
            assert generic.tbl_exists(con=con, tbl_name=tbl, tbl_type="temp")

        # test the schemas

        sm_sample_schema = {
            "detection": pl.Utf8,
            "samplecode": pl.Utf8,
            "color": pl.Utf8,
            "varietal": pl.Utf8,
            "wine": pl.Utf8,
            "id": pl.Utf8,
        }

        cs_sample_schema = {
            "id": pl.Utf8,
            "mins": pl.Float64,
            "wavelength": pl.Int32,
            "absorbance": pl.Float64,
        }

        sm_sample = con.execute(f"SELECT * FROM {sm_sample_tblname}").pl()
        cs_sample = con.execute(f"SELECT * FROM {cs_sample_tblname}").pl()

        assert sm_sample.schema == sm_sample_schema
        assert cs_sample.schema == cs_sample_schema

        # ensure that the number of distinct ids in both match 'n'

        sm_distinct_id_n = con.execute(
            f"SELECT COUNT(DISTINCT({join_key})) FROM {sm_sample_tblname}"
        ).fetchone()[0]
        cs_distinct_id_n = con.execute(
            f"SELECT COUNT(DISTINCT({join_key})) FROM {cs_sample_tblname}"
        ).fetchone()[0]

        assert sm_distinct_id_n == n
        assert cs_distinct_id_n == n

    except Exception as e:
        raise e
    finally:
        stg.cleanup()
