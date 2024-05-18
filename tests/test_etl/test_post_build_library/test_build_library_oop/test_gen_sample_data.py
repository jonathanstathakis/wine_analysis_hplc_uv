"""
Test the `gen_sample_test_data.SampleTableGenerator` class
"""

import duckdb as db
import polars as pl
from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import generic

from tests.test_etl.test_post_build_library.test_build_library_oop import (
    gen_sample_test_data,
)

import pytest

pytest.skip(allow_module_level=True, reason="tests using this have been depreceated..")


def test_sample_table_generator(
    con: db.DuckDBPyConnection,
    stg: gen_sample_test_data.SampleTableGenerator,
):
    """
    Test SampleTableGenerator by asserting that the output schema and the number of
    unique samples matches the expectation
    """
    try:
        stg.gen_samples()
        # test if they exist, if they match the expected schema, and number of distinct ids.

        # test if the new tables exist as temp tables

        sm_sample_tblname = stg.tblnames["sm_sample"]
        cs_sample_tblname = stg.tblnames["cs_sample"]
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
        ).fetchone()[
            0
        ]  # type: ignore
        cs_distinct_id_n = con.execute(
            f"SELECT COUNT(DISTINCT({join_key})) FROM {cs_sample_tblname}"
        ).fetchone()[
            0
        ]  # type: ignore

        assert sm_distinct_id_n == n
        assert cs_distinct_id_n == n

    except Exception as e:
        raise e
    finally:
        stg.cleanup()
