"""
A replacement of earlier Python heavy tests. Simply run the macros and verify that the table dimensions are as expected. Nulls should be considered but i dont know how to easily integrate without further melting.

Current dimensions are as follows:

┌───────────────────────────┬──────────────┬────────────────┐
│        table_name         │ column_count │ estimated_size │
│          varchar          │    int64     │     int64      │
├───────────────────────────┼──────────────┼────────────────┤
│ chromatogram_spectra_long │            7 │      173048494 │
│ sample_metadata           │            9 │            175 │
└───────────────────────────┴──────────────┴────────────────┘
"""

import pytest
import duckdb as db
from wine_analysis_hplc_uv import definitions
from pathlib import Path
import logging

from wine_analysis_hplc_uv.etl.post_build_library import pbl_state_creation

logger = logging.getLogger(__name__)

# the expected shape of cs long after its creation query
CS_LONG_SHAPE_EXPECTED = (173_048_494, 5)
SM_SHAPE_EXPECTED = (175, 8)


@pytest.fixture(scope="module")
def sql_scripts_dir():
    return Path(definitions.PBL) / "queries"


@pytest.fixture(scope="module")
def create_cs_long_script_fpath(sql_scripts_dir: str) -> str:
    return str(Path(sql_scripts_dir) / "create_cs_long.sql")


@pytest.fixture(scope="module")
def create_cs_query(create_cs_long_script_fpath: str):
    """
    return the create cs query string, replace the create with a select
    """

    with open(create_cs_long_script_fpath, "r") as f:
        query = f.read()
    return query


@pytest.fixture(scope="module")
def create_sm_script_fpath(sql_scripts_dir: str) -> str:
    return str(Path(sql_scripts_dir) / "create_sample_metadata.sql")


@pytest.fixture(scope="module")
def create_sm_query(create_sm_script_fpath: str):
    """
    return the create cs query string, replace the create with a select
    """

    with open(create_sm_script_fpath, "r") as f:
        query = f.read()
    return query


def test_create_sample_metadata(
    testcon: db.DuckDBPyConnection,
    create_sm_query: str,
):
    """
    test the creation of the sample metadata table
    """
    try:
        testcon.begin()
        testcon.sql("drop table pbl.sample_metadata")

        testcon.sql(create_sm_query)

        sm = testcon.sql("select * from pbl.sample_metadata")

        expected_shape = (175, 8)

        assert sm.shape == expected_shape

    except Exception as e:
        raise e
    finally:
        testcon.rollback()


def test_create_cs_long(testcon: db.DuckDBPyConnection, create_cs_query: str):
    """
    test the creation of the cs long table by checking against an expected shape
    """
    output_tbl = "pbl.chromatogram_spectra_long"

    try:
        logger.info("beginning transaction..")

        testcon.begin()

        logger.info(f"dropping {output_tbl}..")
        testcon.sql(f"drop table {output_tbl}")

        logger.info("running query..")
        testcon.sql(create_cs_query)

        logger.info(f"retrieving {output_tbl} as a relation..")
        cs = testcon.sql(f"select * from {output_tbl}")

        cs_shape_actual = cs.shape
        expected_cs_shape = CS_LONG_SHAPE_EXPECTED

        logger.info("comparing shape to expectation..")
        logger.info(f"{cs_shape_actual=}, {expected_cs_shape}..")
        assert cs.shape == expected_cs_shape

    except Exception as e:
        raise e
    finally:
        testcon.rollback()


def test_pbl_state_creation(testcon: db.DuckDBPyConnection):
    """
    test moving from 'build_library' state to 'post_build_library' state
    """

    # to test, going to begin a transaction, drop the output tables, then write them and check the output against expectation.

    schema_name = "pbl"
    cs_in_db = "pbl.chromatogram_spectra_long"
    sm_in_db = "pbl.sample_metadata"

    try:
        testcon.begin()

        # drop the schema
        testcon.sql(f"drop schema {schema_name} cascade;")

        # run the function
        pbl_state_creation.update_library(con=testcon)

        # check the outcome
        sm = testcon.sql(f"select * from {sm_in_db}")
        sm_shape = sm.shape
        logger.info(f"{sm_shape=}..")
        logger.info("asserting that sm shape matches expectation..")

        assert SM_SHAPE_EXPECTED == sm_shape

        cs = testcon.sql(f"select * from {cs_in_db}")
        cs_shape = cs.shape

        logger.info(f"{cs_shape=}, {sm_shape=}..")
        logger.info("asserting that shapes meet expectation..")

        assert CS_LONG_SHAPE_EXPECTED == cs_shape

    except Exception as e:
        raise e
    # finally:
    #     testcon.rollback()


def test_pbl_state_creation_with_query_objs(testcon: db.DuckDBPyConnection):
    """
    same as above, but with objects representing the query strings so i can manipulate
    the order easily, and apply string replacement locally.
    """

    queries = [
        "drop schema pbl cascade;",
        pbl_state_creation._create_pbl_schema(),
        pbl_state_creation._sample_metadata_create_as_cte(),
        pbl_state_creation._pbl_cs_long_as_cte(),
    ]

    # now, we're going to try this outside of a transaction. to do so we'll need to replace "pbl" with "test_sch".
    modified_queries = [query.replace("pbl", "test_sch") for query in queries]
    try:
        testcon.begin()
        testcon.sql("SET memory_limit = '20GB';")
        testcon.sql("SET max_memory = '20GB';")
        # execute the queries
        for query in modified_queries:
            logger.info("executing query..")
            logger.info(f"query:\n{query}\n")
            testcon.execute(query)
            logger.info("finished executing query..")
    except Exception as e:
        raise e
    finally:
        logger.info("finished executing queries..")
        testcon.rollback()
