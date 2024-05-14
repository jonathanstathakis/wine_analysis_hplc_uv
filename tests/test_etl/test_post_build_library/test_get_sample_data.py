import pytest
from wine_analysis_hplc_uv import queries
from tests.test_etl.test_post_build_library import gen_sample_test_data
import duckdb as db
import polars as pl


@pytest.mark.parametrize(
    [
        "get_cs_data",
        "filter",
    ],
    [
        (True, queries.Filter(wavelength=(256, 256), color="red")),
        (False, queries.Filter(color="red")),
    ],
)
def test_get_sample_data(
    con: db.DuckDBPyConnection,
    stg_with_gen_samples: gen_sample_test_data.SampleTableGenerator,
    get_cs_data: bool,
    filter: queries.Filter,
):
    """
    # Tests

    TODO: write tests for the below options
    - detection
    - samplecode
    - color
    - varietal
    - wine
    - id
    - mins
    - wavelength

    To test every possible, would need to input for each: null value, one scalar, one iterable.

    Too much work. I reckon its working fine.
    """

    # initialise a GetSampleData with the input filter and test tables
    gsd = queries.GetSampleData(
        filter=filter,
        get_cs_data=get_cs_data,
        cs_tblname=stg_with_gen_samples.tblnames["cs_sample"],
        metadata_tblname=stg_with_gen_samples.tblnames["sm_sample"],
    )

    # retrieve the output df
    df: pl.DataFrame = gsd.run_query(con=con)  # type: ignore

    assert not df.is_empty()

    # assert that the output df matches the expected schema
    expected_schema = {
        "detection": pl.Utf8,
        "samplecode": pl.Utf8,
        "color": pl.Utf8,
        "varietal": pl.Utf8,
        "wine": pl.Utf8,
        "id": pl.Utf8,
        "mins": pl.Float64,
        "wavelength": pl.Int32,
        "absorbance": pl.Float64,
    }
    if get_cs_data:
        assert df.schema == expected_schema
    else:
        assert df.schema == {
            key: val
            for key, val in expected_schema.items()
            if key not in ["wavelength", "absorbance", "mins"]
        }
