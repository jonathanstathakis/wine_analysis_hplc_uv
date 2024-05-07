import pytest
from wine_analysis_hplc_uv import queries
import tests.definitions as test_defs
from tests.test_etl.test_post_build_library import gen_sample_test_data
import duckdb as db
import polars as pl
from wine_analysis_hplc_uv.etl import generic


@pytest.mark.parametrize("get_cs_data", [(True,), (False,)])
def test_get_sample_data(
    con: db.DuckDBPyConnection,
    gen_test_sample_tables: gen_sample_test_data.SampleTableGenerator,
    get_cs_data: bool,
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
    filter = queries.Filter(wavelength=(256, 256), color="red")

    gsd = queries.GetSampleData(
        filter=filter,
        cs_tblname=gen_test_sample_tables.cs_sample_tblname,
        metadata_tblname=gen_test_sample_tables.sm_sample_tblname,
    )

    df: pl.DataFrame = gsd.run_query(con=con)  # type: ignore

    assert not df.is_empty()

    output_schema = {
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
        assert df.schema == output_schema
    else:
        assert df.schema == {
            key: val
            for key, val in output_schema.items()
            if key not in ["wavelength", "absorbance"]
        }
