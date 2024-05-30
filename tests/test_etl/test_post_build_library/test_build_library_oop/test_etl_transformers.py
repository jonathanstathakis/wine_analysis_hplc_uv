"""
2024-05-01 09:30:07 - A module to test extraction of a given dataset from the database. This has required engineering as common queries are potentially too large for duckdb to handle, and thus predicate pushdown needs to be handled carefully.
2024-05-01 09:30:48 - The original data_extract involves the following tables: "c_sample_tracker", "c_cellar_tracker", "c_chemstation_metadata", "chromatogram_spectra".  To generate test data, get 5 wine ids then pull their rows from each table, export as csv to this module.
2024-05-16 08:30:08 - probably going to mark this for depreceation, am rapidly moving towards a SQL heavily workflow.
2024-05-19 00:32:47 - now declared defunct, a direct sql approach has been chosen instead, as state management can be proviced directly, and having to account for edge cases in Python is burdonsome. Furthermore, making this test work has become impossible in the current implementation, and will be marked as skip.
"""

import logging
import duckdb as db
import polars as pl
import pytest
from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import (
    generic,
)
from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import (
    transformers as etl_tformers,
)

logger = logging.getLogger(__name__)

pytest.skip(
    "modules being tested have been depreceated and the tests are not currently usable",
    allow_module_level=True,
)


def write_cs_sample(con: db.DuckDBPyConnection, n: int = 5) -> str:
    """
    Create a temporary table of the long form chromatogram spectra of samples equal to n.

    :returns: the name of the created table
    :return type: str
    """
    cs_tblname = "cs_long_sample"
    con.execute(
        f"""--sql
        CREATE TEMP TABLE {cs_tblname}
        AS (
                SELECT
                    *
                FROM
                    chromatogram_spectra_long
                WHERE
                    id IN (
                    SELECT
                        DISTINCT(id)
                    FROM
                        chromatogram_spectra_long
                    USING
                        SAMPLE {n}
                    )

    )
    """
    )

    return cs_tblname


@pytest.mark.parametrize(
    "tbl_1, tbl_2, tbl_type",
    [
        ("tab_1_base", "tab_2_base", "base"),
        ("tab_1_temp", "", "temp"),
        ("tbl_base", "tbl_temp", "either"),
    ],
)
def test_tbl_exists(
    testcon: db.DuckDBPyConnection,
    tbl_1: str,
    tbl_2: str,
    tbl_type: str,
):
    """
    test whether `tbl_exists` method returns False if a table does not exist in a given database, else True
    """
    # check if base table exists
    if tbl_type == "base":
        try:
            testcon.execute(f"CREATE TABLE {tbl_1} (i INTEGER)")
            assert generic.tbl_exists(testcon, tbl_name=tbl_1, tbl_type=tbl_type)
            assert not generic.tbl_exists(testcon, tbl_name=tbl_2, tbl_type=tbl_type)
        except Exception as e:
            raise e
        finally:
            testcon.execute(f"DROP TABLE {tbl_1}")

    # check if temp table is correctly detected
    if tbl_type == "temp":
        try:
            testcon.execute(f"CREATE TEMP TABLE {tbl_1} (i INTEGER)")
            assert generic.tbl_exists(testcon, tbl_name=tbl_1, tbl_type=tbl_type)
        except Exception as e:
            raise e
        finally:
            testcon.execute(f"DROP TABLE {tbl_1}")

    # pass if temp table and base table are detected
    if tbl_type == "either":
        try:
            testcon.execute(f"CREATE TABLE {tbl_1} (i INTEGER)")
            testcon.execute(f"CREATE TEMP TABLE {tbl_2} (i INTEGER)")
            assert generic.tbl_exists(testcon, tbl_name=tbl_1, tbl_type=tbl_type)
            assert generic.tbl_exists(testcon, tbl_name=tbl_2, tbl_type=tbl_type)
        except Exception as e:
            raise e
        finally:
            testcon.execute(f"DROP TABLE {tbl_1}")
            testcon.execute(f"DROP TABLE {tbl_2}")


def sample_cs_wide(con: db.DuckDBPyConnection, tbl_name: str = "sample_cs", n: int = 5):
    """
    Extract n samples from "chromatogram_spectra", stored as a temporary table for the session. Returns a Polars DataFrame of the sample table.

    :param n: number of samples to include, defaults to 5.
    :type n: int
    :return: The wide form "chromatogram_specta" table as a duckdb relation object
    :type return: DuckDBPyRelation
    """
    con.sql(
        f"""--sql
            SELECT
                id
            FROM
                chromatogram_spectra
            USING
                SAMPLE {n}
        """,
    ).set_alias("cs_id_sample")  # type: ignore

    cs_sample = con.sql(
        f"""--sql
        with cs_id_sample as (select id from chromatogram_spectra using sample {n})
        SELECT
            *
        FROM
            chromatogram_spectra
        WHERE
            id
        IN (
        SELECT
            *
        FROM
            cs_id_sample
            )
        """
    ).set_alias("cs_sample")

    con.execute(f"CREATE TEMP TABLE {tbl_name} AS (SELECT * FROM cs_sample)")

    return cs_sample.pl()


def test_sample_cs_wide(testcon: db.DuckDBPyConnection):
    """
    Test whether `sample_cs_wide` works by calculating the unique ids from the resulting table and comparing. if works, n=n unique(id)
    """

    n = 5
    tbl_name = "cs_sample"
    _ = sample_cs_wide(con=testcon, n=n, tbl_name=tbl_name)

    # get the count of unique ids from the table
    n_samples = testcon.execute(
        f"SELECT COUNT(DISTINCT(id)) FROM {tbl_name}"
    ).fetchone()[0]

    assert n_samples == n


# parametrize docs - <https://docs.pytest.org/en/7.1.x/how-to/parametrize.html>


@pytest.mark.parametrize(
    "write_to_db",
    [
        (True, False),
    ],
)
def test_cs_wide_to_long(
    testcon: db.DuckDBPyConnection,
    write_to_db: bool,
    test_schema_name: str = "test_schema_wide_to_long",
    sample_tbl_name: str = "chromatogram_spectra_sample",
    output_tbl_name: str = "chromatogram_spectra_long",
) -> None:
    """
    Test the user facing function.
    """

    try:
        testcon.begin()

        # craete thee schema
        testcon.execute(f"create schema {test_schema_name}")

        # create the sampling
        _ = sample_cs_wide(con=testcon, tbl_name=sample_tbl_name)

        full_sample_tblname = test_schema_name + sample_tbl_name
        full_output_tblname = test_schema_name + output_tbl_name

        # run the query
        cswtl = etl_tformers.CSWideToLong(
            input_tblname=full_sample_tblname,
            output_tblname=full_output_tblname,
            write_to_db=write_to_db,
        )

        cswtl.run(con=testcon)

        # if write_to_db is false, 'new_tbl_name' should not be present in the database, and result should match the predefined long schema.
        present_in_db = generic.tbl_exists(
            con=testcon, tbl_name=full_output_tblname, tbl_type="either"
        )
        # if write_to_db is False expect present_in_db to be None
        if not write_to_db:
            result = testcon.sql(f"SELECT * FROM {full_output_tblname}_temp").pl()
            if present_in_db is not None:
                assert False
        else:
            result = testcon.sql(f"SELECT * FROM {full_output_tblname}").pl()
            if present_in_db is None:
                assert False

        # get the resulting table

        # result should match the predefined long schema.

        long_schema = {
            "id": pl.Utf8,
            "mins": pl.Float64,
            "wavelength": pl.Int32,
            "absorbance": pl.Float64,
        }

        assert result.schema == long_schema

    except Exception as e:
        raise e

    finally:
        # cleanup by deleting the table IF "write_to_db" is True

        testcon.rollback()


@pytest.mark.parametrize(
    "write_to_db",
    [
        (True, False),
    ],
)
def test_build_sample_metadata(
    testcon: db.DuckDBPyConnection,
    write_to_db: bool,
    test_tblname: str = "sample_metadata",
):
    """
    Test the creation of the join table "sample_metadata"
    """

    # if the table currently exists in the database, rename it to preserve it during the
    # test, then name it back later.
    try:
        bsm = etl_tformers.BuildSampleMetadata(
            write_to_db=write_to_db,
            output_tblname=test_tblname,
            overwrite=True,
        )
        # begin the transaction
        testcon.begin()
        # drop the output table
        testcon.execute(f"drop table {test_tblname}")
        bsm.run(con=testcon)
        if write_to_db:
            assert generic.tbl_exists(con=testcon, tbl_name=test_tblname)
        else:
            assert generic.tbl_exists(
                con=testcon, tbl_name=test_tblname, tbl_type="base"
            )

        assert (
            testcon.sql(f"SELECT COUNT(*) FROM {test_tblname}").fetchone()[0]
            == conftest.NUM_SAMPLES
        )
    except Exception as e:
        raise e

    finally:
        testcon.rollback()
