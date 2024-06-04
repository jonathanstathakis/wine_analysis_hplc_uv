"""
Methods for retrieval of data post-ETL.
"""

from .etl.post_build_library.pbl_oop import generic
from typing import Literal, get_args
import duckdb as db
import pandas as pd
import polars as pl
from typing import Any
from deprecated import deprecated

deprecated(
    reason="depreacted in favor of direct sql queries. Use those instead, either read or strings or literals within a python file."
)

default_filter = dict(
    wavelength=dict(
        value=(256, 256),
        operator="BETWEEN",
    ),
    color=dict(value="red", operator="="),
)

return_frame_type_args = Literal["polars", "pandas", "temp"]

Filter = dict[str, dict[str, Any]]

# filter keys
VALUE = "value"
OPERATOR = "operator"


class GetSampleData:
    def __init__(
        self,
        get_cs_data: bool = True,
        return_frame_type: return_frame_type_args = "polars",
        metadata_tblname: str = "sample_metadata",
        cs_tblname: str = "chromatogram_spectra_long",
        join_key: str = "id",
    ):
        """
        Retrieve sample metadata and optional chromatogram spectral data as one table. Samples are selected
        through the use of the `filter` argument.

        ## Sample Selection

        The `filter` parameter is used to select included samples according to metadata such as 'color', 'varietal',
        and 'wavelength' and 'time' (mins) ranges of their chromato-spectral images.

        ### Dataset Description

        The dataset consists of samples with metadata fields possessing values. The user
        provides keys with values corresponding to desired datasets.

        ### Input Types

        Valid `filter` inputs consist of ranges, scalars or iterables.

        #### Range Fields

        Wavelength and mins are considered 'range' fields, and must be a two element tuple
        of start and end range bounds.

        #### Scalars and Iterables

        All fields, excluding 'mins' and 'wavelength', can possess either a scalar `str` or
        an iterable (`list` or `tuple`) of `str`. If scalar `str`, it will return samples
        possessing that field value.

        ### Optional Arguments

        All `filter` arguments are optional, however the query will take a long time, especially if `wavelength`
        and `mins` ranges are large, hence why the default wavelength value is 256.

        ### Example

        TODO: add example

        :param filter: a mapping of dataset column names to values. Columns in table 'sample_metadata' are
        used to select by sample metadata such as color or varietal, columns in 'chromatogram_spectra_long'
        are used to select the extent of the chromato-spectral image., defaults to default_filter
        :type filter: Filter | dict, optional
        :param get_cs_data: Whether or not to return the chromato-spectral image data. Use when exploring the
        sample metadata prior to a final query. Note that including 'mins' and/or 'wavelength' fields in 'filter'
        will raise an Error, defaults to True
        :type get_cs_data: bool, optional
        :param return_frame_type: _description_, defaults to "polars"
        :type return_frame_type: Literal[&quot;polars&quot;, &quot;pandas&quot;, &quot;temp&quot;], optional
        :param metadata_tblname: the table name containing the sample metadata, defaults to "sample_metadata"
        :type metadata_tblname: str, optional
        :param cs_tblname: the table name containing the chromato-spectral images, defaults to "chromatogram_spectra_long"
        :type cs_tblname: str, optional
        :param join_key: the column name of the key column linking the sample metadata and chromato-spectral tables, defaults to "id"
        :type join_key: str, optional
        """

        self.get_cs_data = get_cs_data
        self.return_frame_type = return_frame_type
        self.metadata_tblname = metadata_tblname
        self.cs_tblname = cs_tblname
        self.join_key = join_key

        self.cs_range_fields = ["mins", "wavelength"]

    def _validate_filter(
        self, filter
    ) -> dict[str, dict[str, str | int | list | float | tuple]]:
        """
        Expect a dict with a string key and a nested dict, also with a string key, and a value of either str, int, list, float or tuple datatype.
        """

        # field parameter keys

        # 0. Check types

        type_validated_filter = self._validate_input_filter_types(filter=filter)

        # 1. Check values

        type_and_value_validated_filter = self._validate_input_filter_values(
            filter=type_validated_filter
        )

        # TODO: wrap string inputs in single quotes to make them valid for the query, otherwise the parser thinks they are column names

        sanitized_filter = self._sanitize_string_values(
            filter=type_and_value_validated_filter
        )

        return sanitized_filter

    def _validate_input_filter_values(self, filter: Filter) -> Filter:
        """
        Validate the input filter values against expectations. Differs from the similar '..types' method in that this checks values only

        """

        expected_field_parameter_keys = [VALUE, OPERATOR]

        # assert value dict keys are in ['value', 'operator']
        for key, val in filter.items():
            assert (
                list(val.keys()) == expected_field_parameter_keys
            ), f"expect nested dict keys to be in {expected_field_parameter_keys}"

        # check if filter content matches expectation if 'get_cs_data' flag is True.
        filter = self._validate_get_cs_data_option_match_filter_input(filter=filter)

        return filter

    def _validate_input_filter_types(self, filter: Filter) -> Filter:
        """
        Check that the filter data types correspond to expectations
        """

        # 0. ensure it is a dict
        assert isinstance(filter, dict), "expect a dict"

        for key, val in filter.items():
            # 1. assert all top level keys are strings
            assert isinstance(key, str), "expect string keys"

            # 2. assert all top level values are dicts
            assert isinstance(val, dict), "expect dict values"

            # 3. assert that they are not empty dicts
            assert val

            # dict of ['value', 'operator'], each have to be treated differently.
            # value is one of str, int, list, float or tuple.
            # operator is a string.

            for kk, vv in val.items():
                # 4. assert nested dict keys are strings
                assert isinstance(kk, str), "expect nested dict keys to be string"

                # 5. assert that the nested val is not empty
                assert vv

            # 7. assert 'value' value is string, int, float, list, or tuple
            expected_datatypes = (str, int, list, float, tuple)
            assert isinstance(
                val[VALUE], expected_datatypes
            ), f"expect nested dict 'value' values to be of one of the following datatypes: {expected_datatypes}"

            # 8. assert that operator is string
            assert isinstance(
                val[OPERATOR], str
            ), f"expect nested dict {OPERATOR} value to be string"

            # 9. assert that operator is not empty string

            assert val[OPERATOR], f"expect nested dict {OPERATOR} value to not be empty"

        return filter

    def _sanitize_string_values(self, filter: Filter) -> Filter:
        """
        wrap string inputs in single quotes to make them valid for the query, otherwise the parser thinks they are column names
        TODO: skip sanitation if strings are already wrapped in single quotes
        """

        sanitized_filter = filter.copy()

        # param_key is a column name, say wavelength, color, etc. param_val is
        # one of 'value', 'operator'
        for param_key, param_val in filter.items():
            for key, val in param_val.items():
                # replacing value strings
                if key == VALUE:
                    input_value = param_val[VALUE]
                    # if input_value is a string, set it directly after wrapping
                    if isinstance(input_value, str):
                        sanitized_filter[param_key][key] = f"'{input_value}'"
                    # if value is an iterable (read: list or tuple), wrap the values in single quotes and return as the same type
                    elif isinstance(input_value, (list, tuple)):
                        interm_iter_val = [f"'{iter_val}'" for iter_val in input_value]
                        # if tuple, return as tuple
                        if isinstance(input_value, tuple):
                            sanitized_filter[param_key][key] = tuple(interm_iter_val)
                        # else its a list
                        else:
                            sanitized_filter[param_key][key] = interm_iter_val

                else:
                    # set operator the same
                    sanitized_filter[param_key][key] = val

        return sanitized_filter

    @property
    def return_frame_type(self):
        return self._return_frame_type

    @return_frame_type.setter
    def return_frame_type(self, val):
        """
        TODO: implement `return_frame_type`
        """
        if val != "polars":
            if val in ["pandas", "temp"]:
                raise NotImplementedError("only 'polars' is currently implemented")
            else:
                raise ValueError(
                    f"please input one of {get_args(return_frame_type_args)} for `return_frame_type`"
                )

        self._return_frame_type = val

    @return_frame_type.getter
    def return_frame_type(self):
        return self._return_frame_type

    def _assemble_query_conditions(self, filter: Filter) -> dict[str, str]:
        """
        Parse the filter to assemble the query conditions. Check if the values are an iterable or scalar, or range fields. Range fields are mins and wavelength. If list, use 'IN' operator, if scalar use '=='. If range use 'BETWEEN' for the left and right values. The range values need to be submitted as a tuple of (start, fin,)

        See <https://duckdb.org/docs/sql/expressions/comparison_operators.html>

        2024-05-14 14:57:13 - want to modify to accept scalar input for all fields. Thus need to modify the logic. Currently mins and wavelength are handled as requiring start and stop values, and use the BETWEEN operator. All other fields are handled either with the IN or '=' operator based on the input type (list, tuple, or not.)  Could simply swap to an input dict containing the operator, a filter parser, leave it up to the user, with some validation, so the input filter would take the form: {'field': {'val':val, 'operator':operator}}, then a simple iteration through to construct the queries.
        2024-05-14 15:03:10 - first move the logic to a function '_parse_filter', test it. Then add defaults, i.e. 'operator' becomes optional, if provided, use (with validation), otherwise add using the aformentioned parsing logic.
        """
        self.queries = {}

        # assumes that iterables inputted possess the __iter__ method, otherwise they are scalar
        # ranges will be iterable though so need to handle them seperately
        key: str
        for key, val in self.filter.items():
            if key in self.cs_range_fields and self.get_cs_data:
                self.queries[key] = (
                    f"{self.cs_tblname}.{key} BETWEEN {val[0]} AND {val[1]}"
                )
            elif isinstance(val, list) or isinstance(val, tuple):
                self.queries[key] = f"{self.metadata_tblname}.{key} IN {tuple(val)}"
            else:
                self.queries[key] = f"{self.metadata_tblname}.{key} = '{val}'"

        return self.queries

    def _assemble_query(self, condition_strings: dict[str, str]) -> str:
        """
        Assemble the query. If get_cs_data is False skip the join, but raise an error if
          values for 'mins' and 'wavelength' are provided in the filter

        :return: a formatted query string
        TODO: rewrite as simply iterating through the values and operator of each item in the filter
        """

        query = []
        query.append(f"SELECT * FROM {self.metadata_tblname}")

        if self.get_cs_data:
            query.append(
                f"LEFT JOIN {self.cs_tblname} ON {self.cs_tblname}.{self.join_key}={self.metadata_tblname}.{self.join_key}"
            )

        for idx, key in enumerate(condition_strings):
            if idx == 0:
                query.append(f"WHERE {condition_strings[key]} ")
            else:
                query.append(f"AND {condition_strings[key]}")

        import sqlparse

        self.query = sqlparse.format(
            " ".join(query), reindent=True, keyword_case="upper"
        )

        return self.query

    def _iterate_through_filter(self, filter: Filter) -> dict[str, str]:
        """
        Iterate through the filter, creating condition strings.

        As it is already validated, simply need to iterate through and assemble a string of the following template:

        WHERE {field name} {operator} {value}

        WHERE {field name} = {value}
        WHERE {field_name} IN {value}
        WHERE {field_name} BETWEEN {value1} AND {value2}
        """

        OPERATOR = "operator"
        VALUE = "value"

        IN = "IN"
        EQUALS = "="
        BETWEEN = "BETWEEN"

        # mapping from the input 'operator' string in the filter dict and the SQL operator

        operators = {IN: "IN", EQUALS: "=", BETWEEN: "BETWEEN"}

        condition_strings = {}

        # iterate through each item, constructing the query based on the value of OPERATOR

        for key, val in filter.items():
            if val[OPERATOR] != BETWEEN:
                condition_strings[key] = (
                    f"{key} {operators[val[OPERATOR]]} {val[VALUE]}"
                )
            elif val[OPERATOR] == BETWEEN:
                condition_strings[key] = (
                    f"{key} {operators[val[OPERATOR]]} {val[VALUE][0]} AND {val[VALUE][1]}"
                )

        assert True
        return condition_strings

    def _validate_get_cs_data_option_match_filter_input(self, filter: Filter):
        """
        raise an error if 'mins', 'wavelength', or 'absorbance' are in the input filter and `get_cs_data` flag is False, as these are fields belonging to the chromato-spectral table, and thus if data from that table is not desired, then inclusion in the filter is invalid.

        TODO: replace this logic with a pre-query to the table(s), comparing the column names with the filter keys. If the cs data is not desired, it will automatically fail as the column names will not match the input filter keys
        """
        if not self.get_cs_data:
            if "mins" in filter:
                if filter["mins"]:
                    raise ValueError(f"{self.get_cs_data=} but 'mins' values provided")
            if "wavelength" in filter:
                if filter["wavelength"]:
                    raise ValueError(
                        f"{self.get_cs_data=} but 'wavelength' values provided"
                    )
            if "absorbance" in filter:
                if filter["absorbance"]:
                    raise ValueError(
                        f"{self.get_cs_data=} but 'absorbance' values provided"
                    )
        return filter

    def run_query(
        self,
        con: db.DuckDBPyConnection,
        filter: Filter = default_filter,
    ) -> pl.DataFrame | pd.DataFrame | None:
        self.con = con

        # validate the input filter, both against the expected structure and initialization flags

        validated_filter = self._validate_filter(filter=filter)

        # validate that the tables are in the database
        self.check_tbls_in_db(con)

        conditions = self._iterate_through_filter(filter=validated_filter)

        # conditions = self._assemble_query_conditions()
        query = self._assemble_query(condition_strings=conditions)

        result = self._query_db(query=query, con=con)

        return result

    def _query_db(self, query: str, con: db.DuckDBPyConnection):
        result = None
        if self.return_frame_type == "polars":
            result = con.execute(query).pl()
        elif self.return_frame_type == "pandas":
            result = con.execute(query).df()
        elif self.return_frame_type == "temp":
            temp_tbl_create_query = f"CREATE TEMP TABLE AS ({query})"
            con.execute(temp_tbl_create_query)
        else:
            raise ValueError("expect one of ['polars','pandas','temp']")
        return result

    def check_tbls_in_db(self, con):
        for tbl in [self.metadata_tblname, self.cs_tblname]:
            tbl_in_db = generic.tbl_exists(con=con, tbl_name=tbl, tbl_type="either")
            if not tbl_in_db:
                raise ValueError(f"{tbl=} not found in db")

    def _validate_filter_input(self):
        """
        validate the input of filter. values can only be scalar, list or tuple.
        """

        for key, val in self.filter.items():
            if hasattr(val, "__iter__"):
                if not isinstance(val, (list, tuple)):
                    raise TypeError(
                        f"If filter values are iterable, only accepting list or tuple, {key} value type: {type(val)}"
                    )
