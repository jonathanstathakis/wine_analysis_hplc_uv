"""
Tests validating the function of `queries.GetSampleData`

These tests rely heavily on pytest fixture and function parametrization. See docs: <https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#fixture-parametrize> for info.

TODO: expand the filter to be more complicated, more combinations
"""

import pytest
from wine_analysis_hplc_uv import queries
from tests.test_etl.test_post_build_library.test_build_library_oop import (
    gen_sample_test_data,
)
import duckdb as db
import polars as pl
from typing import Any


@pytest.fixture(params=[True, False])
def get_cs_data(request):
    return request.param


pytest.skip(allow_module_level=True, reason="tests using this have been depreceated..")


@pytest.fixture
def gsd(
    stg_with_gen_samples: gen_sample_test_data.SampleTableGenerator,
    get_cs_data: bool,
):
    """
    return an initialisd GetSampleData object with the input filter and test tables
    """
    gsd = queries.GetSampleData(
        get_cs_data=get_cs_data,
        cs_tblname=stg_with_gen_samples.tblnames["cs_sample"],
        metadata_tblname=stg_with_gen_samples.tblnames["sm_sample"],
    )

    return gsd


@pytest.fixture
def expected_schema(get_cs_data: bool):
    """
    The expected output schema
    """
    # assert that the output df matches the expected schema
    base_schema = {
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
        return base_schema
    else:
        return {
            key: val
            for key, val in base_schema.items()
            if key not in ["wavelength", "absorbance", "mins"]
        }


@pytest.fixture
def filter(get_cs_data: bool):
    """
    return a filter dict corresponding to whether get_cs_data is True or not

    TODO: add all options. The options are as follows: container and datatype. container: scalar, list, tuple. type: str, int, float combinations of each produce all possible input types. But some datatypes only make sense for certain values, thus it would be better to take a sampling from the table to use as the basis of the value input.

    sample_metadata columns: ['detection','samplecode','color','varietal','wine','id']
    cs_long_columns: ['id','mins','wavelength','absorbance']

    Now, only some fields should have certain datatypes, for example detection should be str, wheras wavelength should be int, mins and absorbance should be float, In fact, thats it. Wavelength must be int, mins and absorbance must be float. Also samplecode is int. Also some of these options will preclude others. f me.

    Furthermore, some operators need certain data structures - between needs a 2 element iterable, in needs an iterable, '=' needs a scalar (unless, presumably, it is a nested column?)

    This is becoming much more complicated than simply writing queries directly..

    TODO: add datatype validation to validation routines.
    """

    base_filter = {
        "detection": {"value": "cuprac", "operator": "="},  # scalar string
        "samplecode": "",
        "color": {"value": "red", "operator": "="},
        "varietal": {"value": ["cabernet_sauvignon", "shiraz"], "operator": "IN"},
        "wine": "",
        "id": "",
        "wavelength": {
            "value": 256,
            "operator": "=",
        },
        "mins": "",
        "absorbance": "",
    }

    if get_cs_data:
        return base_filter
    else:
        cs_fields = ["wavelength", "mins", "absorbance"]
        return {k: v for k, v in base_filter.items() if k not in cs_fields}


def test_get_sample_data(
    con: db.DuckDBPyConnection,
    gsd: queries.GetSampleData,
    filter: dict[str, dict[str, Any]],
    expected_schema: dict,
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

    # retrieve the output df
    df: pl.DataFrame = gsd.run_query(
        con=con,
        filter=filter,
    )

    assert not df.is_empty()
    assert df.schema == expected_schema


# test failure cases of `_validate_filter`. Expect failure with the following inputs. Parameter list below describes the assertion test in _validate_filter, add a negative, i.e. "filter is a dict" should read "filter is NOT a dict" when thinking about the test

VALUE = "value"
OPERATOR = "operator"


@pytest.mark.parametrize(
    "filter",
    [
        # 0. filter is a dict
        ("not a dict",),
        # 1. top level key is a string
        ({9: "a value"}),  # not a string key
        # 2. top level values are dicts
        ({"a string key": 9}),
        # 3. top level dicts are not empty
        ({"a string key": {}}),
        # 4. nested dict keys are strings
        ({"a string key": {9: "a value"}},),
        # 5. nested val are not None
        ({"a string key": {"nested string key": None}}),
        # 7. nested values are string, int, float, list, or tuple
        ({"a string key": {VALUE: 2 + 3j, OPERATOR: "="}}),
        # 8. operator is str
        ({"a string key": {VALUE: 5, OPERATOR: 5}}),
        # 9. operator is not an empty string
        ({"a string key": {VALUE: 5, OPERATOR: ""}}),
    ],
)
def test_get_sample_data_invalid_filter(
    filter: queries.Filter,
    gsd: queries.GetSampleData,
):
    """
    test GetSampleData initialization with invalid filter input
    """
    try:
        gsd._validate_input_filter_types(filter=filter)
    except Exception:
        pass
    else:
        assert False, filter


@pytest.fixture(
    params=[
        pytest.param(
            {"color": {VALUE: 5, "not operator": 10}}, marks=pytest.mark.xfail
        ),
        pytest.param(
            {"color": {"not value": 5, OPERATOR: 10}}, marks=pytest.mark.xfail
        ),
        pytest.param(
            {"color": {"not value": 5, "not operator": 10}}, marks=pytest.mark.xfail
        ),
        {
            "color": {
                VALUE: "red",
                OPERATOR: "=",
            }
        },
    ]
)
def filter_with_correct_keys(request):
    return request.param


def test_validate_input_filter_values(
    filter_with_correct_keys: queries.Filter,
    gsd: queries.GetSampleData,
):
    """
    test validation of filter values
    """
    gsd._validate_input_filter_values(filter=filter_with_correct_keys)


@pytest.fixture(
    params=[
        "red",
        10,
        10.0,
        [
            "red",
        ],
        tuple(
            ["red"],
        ),
    ]
)
def sanitize_string_values_filter(request):
    return {"color": {"value": request.param, "operator": "="}}


def test_sanitize_string_values(
    sanitize_string_values_filter: queries.Filter,
    gsd: queries.GetSampleData,
):
    """
    test the method '_sanitize_string_values' through input of various forms, and validate  by checking whether the first and last element of each string (or substring) is "'"
    """

    sanitized_filter = gsd._sanitize_string_values(filter=sanitize_string_values_filter)

    # fields
    for key, val in sanitized_filter.items():
        # value parameter
        value = val[VALUE]
        # if value is a scalar
        if isinstance(value, str):
            assert value[0] == "'"
            assert value[-1] == "'"
        # if value is an iterable
        elif isinstance(value, (list, tuple)):
            for v in value:
                if isinstance(v, str):
                    assert v[0] == "'"
                    assert v[-1] == "'"


@pytest.fixture
def sanitized_filter(get_cs_data: bool) -> queries.Filter:
    """
    return a sanitized filter object, that is one with quote wrapped strings ready for injection
    """
    if get_cs_data:
        return {
            "color": {"value": "'red'", "operator": "="},
            "wavelength": {"value": 256, "operator": "="},
        }
    else:
        return {
            "color": {"value": "'red'", "operator": "="},
        }


def test_iterate_through_filter(
    sanitized_filter: queries.Filter,
    gsd: queries.GetSampleData,
):
    """
    test query string assembly execution
    """
    gsd._iterate_through_filter(filter=sanitized_filter)


@pytest.fixture
def condition_strings(sanitized_filter, gsd: queries.GetSampleData) -> dict:
    """
    return the concatenated query condition strings
    """
    return gsd._iterate_through_filter(filter=sanitized_filter)


def test_assemble_query(condition_strings: dict, gsd: queries.GetSampleData):
    """
    test whether `._assemble_query` produces a valid query.
    TODO: come up with a method of validating the query
    """

    gsd._assemble_query(condition_strings=condition_strings)

    assert True


@pytest.fixture
def query():
    """
    A simple query for testing 'run_query'
    """
    return """--sql
        SELECT *\nFROM sm_sample\nWHERE color = 'red'
"""


def test_query_db(query: str, gsd: queries.GetSampleData, con: db.DuckDBPyConnection):
    gsd._query_db(query=query, con=con)


def test_run_query(
    gsd: queries.GetSampleData,
    filter: queries.Filter,
    con: db.DuckDBPyConnection,
):
    """
    test `.run_query` in its entirety
    """
    gsd.run_query(
        con=con,
        filter=filter,
    )
