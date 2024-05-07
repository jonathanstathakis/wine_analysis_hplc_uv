"""
2024-05-01 09:30:07

A module to test extraction of a given dataset from the database. This has required engineering as common queries are potentially too large for duckdb to handle, and thus predicate pushdown needs to be handled carefully.

TODO:
- [x] define dummy database
- [ ] define new query class

2024-05-01 09:30:48

The original data_extract involves the following tables:

- "c_sample_tracker"
- "c_cellar_tracker"
- "c_chemstation_metadata"
- "chromatogram_spectra"

To generate test data, get 5 wine ids then pull their rows from each table, export as csv to this module.
"""

from wine_analysis_hplc_uv.etl import generic, transformers as etl_tformers
import duckdb as db
import pytest
import logging

logger = logging.getLogger(__name__)


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
    con: db.DuckDBPyConnection,
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
            con.execute(f"CREATE TABLE {tbl_1} (i INTEGER)")
            assert generic.tbl_exists(con, tbl_name=tbl_1, tbl_type=tbl_type)
            assert not generic.tbl_exists(con, tbl_name=tbl_2, tbl_type=tbl_type)
        except Exception as e:
            raise e
        finally:
            con.execute(f"DROP TABLE {tbl_1}")

    # check if temp table is correctly detected
    if tbl_type == "temp":
        try:
            con.execute(f"CREATE TEMP TABLE {tbl_1} (i INTEGER)")
            assert generic.tbl_exists(con, tbl_name=tbl_1, tbl_type=tbl_type)
        except Exception as e:
            raise e
        finally:
            con.execute(f"DROP TABLE {tbl_1}")

    # pass if temp table and base table are detected
    if tbl_type == "either":
        try:
            con.execute(f"CREATE TABLE {tbl_1} (i INTEGER)")
            con.execute(f"CREATE TEMP TABLE {tbl_2} (i INTEGER)")
            assert generic.tbl_exists(con, tbl_name=tbl_1, tbl_type=tbl_type)
            assert generic.tbl_exists(con, tbl_name=tbl_2, tbl_type=tbl_type)
        except Exception as e:
            raise e
        finally:
            con.execute(f"DROP TABLE {tbl_1}")
            con.execute(f"DROP TABLE {tbl_2}")


def sample_cs_wide(con: db.DuckDBPyConnection, tbl_name: str = "sample_cs", n: int = 5):
    """
    Extract n samples from "chromatogram_spectra", stored as a temporary table for the session. Returns a Polars DataFrame of the sample table.

    :param n: number of samples to include, defaults to 5.
    :type n: int
    :return: The wide form "chromatogram_specta" table as a duckdb relation object
    :type return: DuckDBPyRelation
    """
    cs_id_sample = con.sql(
        f"""--sql
            SELECT
                id
            FROM
                chromatogram_spectra
            USING
                SAMPLE {n}
        """,
    ).set_alias(
        "cs_id_sample"
    )  # type: ignore

    cs_sample = con.sql(
        """--sql
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


def test_sample_cs_wide(con: db.DuckDBPyConnection):
    """
    Test whether `sample_cs_wide` works by calculating the unique ids from the resulting table and comparing. if works, n=n unique(id)
    """

    n = 5
    tbl_name = "cs_sample"
    _ = sample_cs_wide(con=con, n=n, tbl_name=tbl_name)

    # get the count of unique ids from the table
    n_samples = con.execute(f"SELECT COUNT(DISTINCT(id)) FROM {tbl_name}").fetchone()[0]

    assert n_samples == n


# parametrize docs - <https://docs.pytest.org/en/7.1.x/how-to/parametrize.html>


@pytest.mark.parametrize(
    "write_to_db",
    [
        (True, False),
    ],
)
def test_cs_wide_to_long(
    con: db.DuckDBPyConnection,
    write_to_db: bool,
    sample_tbl_name: str = "cs_sample",
    new_tbl_name: str = "cs_sample_long",
) -> None:
    """
    Test the user facing function.
    """
    if generic.tbl_exists(con=con, tbl_name=sample_tbl_name):
        raise ValueError(f"{sample_tbl_name=} already exists!")

    # create the sample table

    _ = sample_cs_wide(con=con, tbl_name=sample_tbl_name)

    # create the transform table

    cswtl = etl_tformers.CSWideToLong(
        input_tblname=sample_tbl_name,
        output_tblname=new_tbl_name,
        write_to_db=write_to_db,
    )

    cswtl.run(con=con)

    import polars as pl

    # if write_to_db is false, 'new_tbl_name' should not be present in the database, and result should match the predefined long schema.

    try:
        present_in_db = generic.tbl_exists(con=con, tbl_name=sample_tbl_name)

        # if write_to_db is False expect present_in_db to be None
        if not write_to_db:
            result = con.sql(f"SELECT * FROM {new_tbl_name}_temp").pl()
            if present_in_db is not None:
                assert False
        else:
            result = con.sql(f"SELECT * FROM {new_tbl_name}").pl()
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

        cswtl.cleanup()


@pytest.mark.parametrize(
    "write_to_db",
    [
        (True, False),
    ],
)
def test_build_sample_metadata(
    con: db.DuckDBPyConnection,
    write_to_db: bool,
    test_tblname: str = "sample_metadata_test",
):
    """
    Test the creation of the join table "sample_metadata"
    """

    bsm = etl_tformers.BuildSampleMetadata(
        write_to_db=write_to_db,
        output_tblname=test_tblname,
        overwrite=True,
    )

    bsm.run(con=con)
    if write_to_db:
        assert generic.tbl_exists(con=con, tbl_name=test_tblname)
    else:
        assert generic.tbl_exists(
            con=con, tbl_name=test_tblname + "_temp", tbl_type="temp"
        )

    bsm.cleanup()
