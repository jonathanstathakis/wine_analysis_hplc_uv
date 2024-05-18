"""
2024-05-01 13:26:43 - New master module to replace old dataextract. Contains methods to extract relevent fields from the tables in wines.db through a user-friendly class
"""

# first ensure that chromatogram_spectrum is in long form as the rest of the functionality assumes this
from pathlib import Path
import numpy as np
import polars as pl
import logging
import duckdb as db
from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import (
    generic,
)
from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import etl_pipeline

logger = logging.getLogger(__name__)


class ETLTransformerMixin(etl_pipeline.ETLTransformerABC):
    @property
    def write_to_db(self):
        return self._write_to_db

    @write_to_db.setter
    def write_to_db(self, val: bool):
        self._write_to_db = val

    @write_to_db.getter
    def write_to_db(self):
        return self._write_to_db

    @property
    def overwrite(self):
        return self._overwrite

    @overwrite.setter
    def overwrite(self, val: bool):
        self._overwrite = val

    @overwrite.getter
    def overwrite(self):
        return self._overwrite


def cs_wide_schema():
    cs_label_cols = {
        "id": pl.Utf8,
        "mins": pl.Float64,
    }
    wavelengths = [f"nm_{x}" for x in np.arange(190, 600, 2)]
    wavelength_schema = {nm: pl.Float64 for nm in wavelengths}
    schema = {**cs_label_cols, **wavelength_schema}

    return schema


class CSWideToLong(ETLTransformerMixin):
    def __init__(
        self,
        input_tblname: str = "chromatogram_spectra",
        output_tblname: str = "chromatogram_spectra_long",
        write_to_db: bool = False,
        overwrite: bool = False,
    ):
        """
        :param con: connection object to the database
        :type con: DuckDBPyConnection

        :param input_tbl_name: the name of the input table, the wide table that needs converting to long-form. Defaults to 'chromatogram_spectra'
        """
        self.input_tblname = input_tblname
        self.output_tblname: str = output_tblname
        self._write_to_db = write_to_db
        self._overwrite = overwrite

        self._interm_tblname = "split_wavelength_col"

        # state flag to be updated when the temp table is written to the db
        self._temp_tbl_written: bool = False

        self.cs_input_schema = cs_wide_schema()

    def run(
        self,
        con: db.DuckDBPyConnection,
    ) -> str:
        """
        Unpivot chromatogram_spectra

        Key function unpivoting "chromatogram_spectra".

        :return: newly written tbl name
        """

        self.con = con

        # check if input table present in db

        with open(Path(__file__).parent.parent / "create_cs_long.sql", "r") as f:
            logger.info("reading cs wide to long query..")
            query = f.read()
        logger.info("executing cs wide to long query..")
        self.con.sql(query).show()

        return "spectrum_chromatogram"

    def _interm_transforms(self) -> None:
        """
        Key function unpivoting "chromatogram_spectra".

        :param con: connection object to the database
        :type con: DuckDBPyConnection

        :param input_tbl_name: the name of the input table, the wide table that needs converting to long-form. Defaults to 'chromatogram_spectra'

        :param new_name_suffix: Optional. A string to add to the end of the NEW table name if desired. Defaults to nothing. The table name has the template: '{input_tbl_name}_long_{new_name_suffix}'
        :type new_name_suffix: str

        :return: a polars dataframe containing the unpivoted data, and a string containing the new table name.
        """

        return None

    def cleanup(self):
        """
        drop the temp and base table if they are written.
        """
        if generic.tbl_exists(self.con, tbl_name=self.output_tblname, tbl_type="temp"):
            self.con.execute(f"DROP TABLE {self.output_tblname}")

        if generic.tbl_exists(self.con, tbl_name=self.output_tblname):
            self.con.execute(f"DROP TABLE {self.output_tblname}")


class BuildSampleMetadata(ETLTransformerMixin):
    def __init__(
        self,
        sample_tracker_tblname: str = "c_sample_tracker",
        cellar_tracker_tblname: str = "c_cellar_tracker",
        chemstation_metadata_tblname: str = "c_chemstation_metadata",
        write_to_db: bool = False,
        output_tblname: str = "sample_metadata",  # TODO: somehow link this to the query itself
        overwrite: bool = False,
    ):
        self.tbl_names = dict(
            sample_tracker=sample_tracker_tblname,
            cellar_tracker=cellar_tracker_tblname,
            chemstation_metadata=chemstation_metadata_tblname,
        )

        self._write_to_db = write_to_db
        self._overwrite = overwrite

        self.output_tblname = output_tblname

    def run(self, con: db.DuckDBPyConnection):
        self.con = con
        with open(Path(__file__).parent / "create_sample_metadata.sql", "r") as f:
            query = f.read()

        con.sql(query)

    def cleanup(self) -> None:
        self.con.execute(f"DROP TABLE {self.output_tblname}")
