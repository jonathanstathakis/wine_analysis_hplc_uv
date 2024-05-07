"""
2023-11-09

Writing a SQL query to replace the functions 'melt_df', 'subset', and 'adjust_df' to decrease total runtime. It will first mantle the sql queries in '2023-10-24.creating_3d_dataset.ipynb' then go from there.

TODO:
- [x] add expression to exclude ('72','98') alongside other outliers.
- [x] replace `get_data()` calls with the new query
"""

import duckdb as db
import pandas as pd
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.peak_deconv import db_interface

from dataclasses import dataclass


@dataclass
class DataExtractor(db_interface.DBInterface):
    """
     Contains methods necessary to extract a dataset from the database.

    Contains 'create_subset_table' which creates a temporary table for the session which can be further manipulated through calls on `self.con_` or extracted as a pandas DataFrame with `get_tbl_as_df`

    NOTE: It is currently necessary to run `load_data` to initialize the object fully.
    """

    _con: db.DuckDBPyConnection
    _table_name: str = "temp_tbl"
    detection: tuple = (None,)
    samplecode: tuple = (None,)
    exclude_samplecodes: tuple = (None,)
    exclude_ids: tuple = tuple(definitions.EXCLUDEIDS.values())
    color: tuple = (None,)
    wavelengths: int | list | tuple = 256
    varietal: tuple = (None,)
    wine: tuple = (None,)
    mins: tuple = (None, None)
    raw_data = None
    _cs_tbl: str = "chromatogram_spectra"

    def get_data(
        self,
    ) -> pd.DataFrame:
        self._create_subset_table()
        self.raw_data = self._get_tbl_as_df()

        return self.raw_data

    def _create_subset_table(
        self,
    ) -> db.DuckDBPyConnection:
        """
        create_subset_table create a temporary table as a multiple join of tables in the db based on values provided for each variable

        Original called Super Table, this function creates a temporary table bound to the current connection session, collecting all the data relevant to a sample within the database. parameters control the extent of the data and are injected into a SQL query. Returns a connection object for further queries, or a DataFrame of the table can be created by following this call with `get_tbl_as_df`.

        :param detection: detection label, either 'cuprac', or 'raw', defaults to (None,)
        :type detection: tuple, optional

        :param samplecode: samplecode strings for desired samples, defaults to (None,)
        :type samplecode: tuple, optional

        :param exclude_samplecodes: samplecode strings of samples not to be included in output, defaults to (None,)
        :type exclude_samplecodes: tuple, optional

        :param exclude_ids: id strings of samples not to be included in output, defaults to (None,)
        :type exclude_ids: tuple, optional

        :param color: color string of desired samples: 'white', 'red', 'rose','orange', defaults to (None,)
        :type color: tuple, optional

        :param wavelengths: wavelength signal number to be extracted, i.e. input 256 as an int, or list or tuple of ints. Set ranges from 190-600nm, but not for all samples. Defaults to "nm_256"
        :type wavelengths: int | list | tuple, optional

        :param varietal: Varietal string to be in output sample set. There are 46 varietals included. Defaults to (None,)
        :type varietal: tuple, optional

        :param wine: wine names of samples to be included in output sample ste, defaults to (None,)
        :type wine: tuple, optional

        :param mins: observation time range of rows in output sampleset, ranging from 0 to 52 or so, defaults to (None, None)
        :type mins: tuple, optional

        :return: connection to the current database session containing the created table
        :rtype: db.DuckDBPyConnection
        """

        cs_col_list = self._select_wavelengths(cs_cols, self.wavelengths)

        from pathlib import Path

        here = Path(__file__).parent
        with open(here / "subset_tbl.sql", "r") as f:
            subset_tbl_query = f.read()

        # Join the data tables together
        self._con.execute(
            query=subset_tbl_query,
            parameters={
                "cs_col_list": cs_col_list,
                "detection": self.detection,
                "samplecode": self.samplecode,
                "exclude_samplecodes": self.exclude_samplecodes,
                "exclude_ids": self.exclude_ids,
                "color": self.color,
                "varietal": self.varietal,
                "wine": self.wine,
                "min_start": self.mins[0],
                "min_end": self.mins[1],
            },
        )
        return self

    def _get_tbl_as_df(self) -> pd.DataFrame:
        """
        get_tbl_as_df extract the table created by `create_subset_table` as a DataFrame

        Simple function to move the table created by `create_subset_table` to Python memory as a pandas DataFrame

        :return: DataFrame
        :rtype: pd.DataFrame
        """

        return self._con.sql(
            f"""--sql
                             SELECT * FROM {self._table_name}
                             """
        ).df()

    def _select_wavelengths(self, wavelengths: int | list) -> list:
        """
        select_wavelengths translate the input int wavelength selection to a list of column labels in form 'nm_*' for injection into the SQL query in `create_subset_table`

        SQL databases generally abhor numerical column labels, thus the individual wavelength columns are labeled with a 'nm_' prefix then the wavelength, i.e. "nm_256". This is however, burdensome for users to enter in `create_subset_table`, thus this function translates the input ints into column labels then passes it to the SQL query for injection. This function goes one step further though, and queries the table for its current wavelength columns then selects from them for the final list. Returns a list of column labels.

        :param columns: columns in the spectrum chromatogram table
        :type columns: pd.DataFrame
        :param wavelengths: wavelengths to be included in output sampleset, i.e. 256, 450.
        :type wavelengths: str | list
        :raises ValueError: if input for `wavelengths` is not an int, list, tuple, or None
        :return: a list of strings of wavelengths, such as 'nm_256'
        :rtype: list
        """

        columns = self._con.execute(
            f"""--sql
                                    SELECT
                                        column_name
                                    FROM
                                        duckdb_columns()
                                    WHERE
                                        table_name='{self._cs_tbl}'
                                        AND
                                        REGEXP_MATCHES(column_name, '^nm_[0-9]+$')
                                    """
        ).df()

        #
        if isinstance(columns, pd.DataFrame):
            if columns.empty:
                self._check_db_for_tbl_exist(self._cs_tbl)
                self._check_db_for_tbl_col_exist(self._cs_tbl)

                raise ValueError("cs_cols query returned an empty table")

        else:
            raise TypeError("Not a pd.DataFrame")

        if isinstance(columns, pd.DataFrame):
            if columns.empty:
                raise ValueError("column df is empty")

        else:
            raise TypeError("input columns var is not a DataFrame")

        columns = columns["column_name"]
        columns = columns.str.split("_", expand=True)
        columns = columns.set_axis(axis=1, labels=["unit", "wavelength"])
        columns = columns.assign(wavelength=lambda df: df["wavelength"].astype(int))

        if isinstance(wavelengths, (list, tuple)):
            columns = columns.query("wavelength in @wavelengths")

        elif wavelengths == "all":
            columns = columns

        elif isinstance(wavelengths, int):
            columns = columns.query("wavelength==@wavelengths")

        else:
            raise ValueError(
                f"expecting list, tuple, int, or None for wavelengths, got{type(wavelengths)}"
            )

        columns = columns.assign(
            tbl_wavelength_strs=columns.loc[:, "unit"]
            + "_"
            + columns.loc[:, "wavelength"].astype(str)
        )

        # turn them into a sql friendly list
        cs_col_list = ", ".join([f"cs.{col}" for col in columns["tbl_wavelength_strs"]])

        return cs_col_list

    def get_first_x_raw_samples(
        self, key: str = "code_wine", x: int = 5
    ) -> pd.DataFrame:
        """
        Return first x rows of the query as a pandas dataframe

        _extended_summary_

        :param x: _description_
        :type x: int
        :return: _description_
        :rtype: pd.DataFrame
        """

        self._create_subset_table()

        # select the 'code_wine' of the first x samples

        first_x_codewines = f"""--sql
        SELECT
            DISTINCT({key})
        FROM
          {self._table_name}
        LIMIT {x}
        """

        get_samples_query = f"""--sql
        SELECT
            *
        FROM
            {self._table_name}
        WHERE
            {key}
        IN
        ({first_x_codewines})
        """

        samples = self._con.query(get_samples_query).df()

        return samples

    def _check_db_for_tbl_col_exist(
        self,
        tbl_name: str,
    ):
        """
        Check if any cols matching the table name are present
        """
        all_cs_cols = self._con.sql(
            f"""
            SELECT
                column_name
            FROM
                duckdb_columns()
            WHERE
                table_name='{tbl_name}'
            """
        ).fetchall()

        if len(all_cs_cols) == 0:
            raise ValueError(f"{tbl_name} tbl is empty")


class RawTestSet3DCreator(DataExtractor):
    """
    Class to replicate the RAW3DSET parquet file
    """

    def __init__(self, db_path: str):
        DataExtractor.__init__(self, db_path=db_path)

        self._create_subset_table(
            wavelengths=list(range(190, 402, 2)),
            detection=("raw",),
            exclude_samplecodes=("72", "98"),
        )

        self.df = self._get_tbl_as_df().dropna()
