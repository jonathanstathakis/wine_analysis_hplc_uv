from tests.test_etl.test_post_build_library.test_build_library_oop import (
    gen_sample_test_data,
)
import pytest
import duckdb as db

from tests.test_etl.test_post_build_library.test_build_library_oop.gen_sample_test_data import (
    GenSampleCSWide,
)


@pytest.fixture
def gen_test_sample_tables(
    testcon: db.DuckDBPyConnection,
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
        con=testcon,
        n=n,
        sample_metadata_tblname=sm_tblname,
        cs_tblname=cs_tblname,
        join_key=join_key,
        sm_sample_tblname=sm_sample_tblname,
        cs_sample_tblname=cs_sample_tblname,
    )
    stg.gen_samples()

    return stg


@pytest.fixture
def gen_sample_cs_wide(testcon: db.DuckDBPyConnection):
    samplegenner = GenSampleCSWide(con=testcon)
    samplegenner.gen_sample_cs_wide()

    return samplegenner


@pytest.fixture
def stg(
    testcon: db.DuckDBPyConnection,
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
    return gen_sample_test_data.SampleTableGenerator(
        con=testcon,
        n=n,
        sample_metadata_tblname=sm_tblname,
        cs_tblname=cs_tblname,
        join_key=join_key,
        sm_sample_tblname=sm_sample_tblname,
        cs_sample_tblname=cs_sample_tblname,
    )


@pytest.fixture
def stg_with_gen_samples(
    stg: gen_sample_test_data.SampleTableGenerator,
) -> gen_sample_test_data.SampleTableGenerator:
    """
    Run stg.gen_samples(), producing a random sampling of metadata and chromato-spectral tables within the test database

    :param stg: an initialised SampleTableGenerator class instance
    :type stg: gen_sample_test_data.SampleTableGenerator
    :return: the initialised SampleTableGenerator class instance
    :rtype: gen_sample_test_data.SampleTableGenerator
    """
    return stg.gen_samples()
