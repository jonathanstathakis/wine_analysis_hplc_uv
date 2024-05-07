"""
Methods for retrieval of data post-ETL.
"""

from .etl import generic
from typing import Literal, TypedDict, get_args
import duckdb as db
import pandas as pd
import polars as pl


class Filter(TypedDict, total=False):
    """
    The object representing the sample selection filter. See `GetSampleData` for more
    information.
    """

    wavelength: tuple[int, int]
    mins: tuple[int, int]
    color: tuple[str, ...] | str
    varietal: tuple[str, ...] | str | None
    wine: tuple[str, ...] | str
    id: tuple[str, ...] | str


default_filter = Filter(
    wavelength=(256, 256),
    color="red",
)

return_frame_type_args = Literal["polars", "pandas", "temp"]


class GetSampleData:
    def __init__(
        self,
        filter: Filter | dict = default_filter,
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

        See `filter` default value, `Filter` type.

        TODO: filter input validation, range fields must be a two element tuple, all others scalars or
        iterables.
        TODO: filter input validation for empty filter - throw an error if an empty filter is provided?,
        include a backend attribute that allows for disabling the error prior to calling `run_query`
        TODO: implement `return_frame_type`

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

        self.filter = filter
        self.get_cs_data = get_cs_data
        self.return_frame_type = return_frame_type
        self.metadata_tblname = metadata_tblname
        self.cs_tblname = cs_tblname
        self.join_key = join_key

        self.cs_range_fields = ["mins", "wavelength"]

    @property
    def return_frame_type(self):
        return self._return_frame_type

    @return_frame_type.setter
    def return_frame_type(self, val):
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

    def _assemble_query_conditions(self) -> dict[str, str]:
        """
        Parse the filter to assemble the query conditions. Check if the values are an iterable or scalar, or range fields. Range fields are mins and wavelength. If list, use 'IN' operator, if scalar use '=='. If range use 'BETWEEN' for the left and right values. The range values need to be submitted as a tuple of (start, fin,)

        See <https://duckdb.org/docs/sql/expressions/comparison_operators.html>
        """
        self.queries = {}

        # assumes that iterables inputted possess the __iter__ method, otherwise they are scalar
        # ranges will be iterable though so need to handle them seperately
        key: str
        for key, val in self.filter.items():
            if key in self.cs_range_fields:
                self.queries[
                    key
                ] = f"{self.cs_tblname}.{key} BETWEEN {val[0]} AND {val[1]}"
            elif isinstance(val, list) or isinstance(val, tuple):
                self.queries[key] = f"{self.metadata_tblname}.{key} IN {tuple(val)}"
            else:
                self.queries[key] = f"{self.metadata_tblname}.{key} = '{val}'"

        return self.queries

    def _assemble_query(self) -> str:
        """
        Assemble the query. If get_cs_data is False skip the join, but raise an error if values for 'mins' and 'wavelength' are provided in the filter

        :return: a formatted query string

        TODO:
        test the following scenarios:
            1. get_cs_data == True
                1. the join is successful
            2. get_cs_data == False
                1. mins and wavelength values are subbmitted to filter, expect ValueError
        """

        if not self.get_cs_data:
            if "mins" in self.filter:
                if self.filter["mins"]:
                    raise ValueError(f"{self.get_cs_data=} but 'mins' values provided")
            if "wavelength" in self.filter:
                if self.filter["wavelength"]:
                    raise ValueError(
                        f"{self.get_cs_data=} but 'wavelength' values provided"
                    )

        conditions = self._assemble_query_conditions()

        query = []
        query.append(f"SELECT * FROM {self.metadata_tblname}")

        if self.get_cs_data:
            query.append(
                f"LEFT JOIN {self.cs_tblname} ON {self.cs_tblname}.{self.join_key}={self.metadata_tblname}.{self.join_key}"
            )

        for idx, key in enumerate(conditions):
            if idx == 0:
                query.append(f"WHERE {conditions[key]} ")
            else:
                query.append(f"AND {conditions[key]}")
        import sqlparse

        self.query = sqlparse.format(
            " ".join(query), reindent=True, keyword_case="upper"
        )

        return self.query

    def run_query(
        self, con: db.DuckDBPyConnection
    ) -> pl.DataFrame | pd.DataFrame | None:
        self.con = con

        # validate that the tables are in the database
        for tbl in [self.metadata_tblname, self.cs_tblname]:
            tbl_in_db = generic.tbl_exists(con=con, tbl_name=tbl, tbl_type="either")
            if not tbl_in_db:
                raise ValueError(f"{tbl=} not found in db")

        query = self._assemble_query()

        result = None
        if self.return_frame_type == "polars":
            result = self.con.execute(query).pl()
        elif self.return_frame_type == "pandas":
            result = self.con.execute(query).df()
        elif self.return_frame_type == "temp":
            temp_tbl_create_query = f"CREATE TEMP TABLE AS ({query})"
            self.con.execute(temp_tbl_create_query)
        else:
            raise ValueError("expect one of ['polars','pandas','temp']")

        return result

    def validate_filter_input(self):
        """
        validate the input of filter. values can only be scalar, list or tuple.
        """

        for key, val in self.filter.items():
            if hasattr(val, "__iter__"):
                if not isinstance(val, (list, tuple)):
                    raise TypeError(
                        f"If filter values are iterable, only accepting list or tuple, {key} value type: {type(val)}"
                    )
