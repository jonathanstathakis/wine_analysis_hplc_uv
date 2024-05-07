"""
2024-05-01 13:26:43

New master module to replace old dataextract.

Contains methods to extract relevent fields from the tables in wines.db through a user-friendly class
"""

# first ensure that chromatogram_spectrum is in long form as the rest of the functionality assumes this
import numpy as np
import polars as pl
import logging
import warnings
import duckdb as db
from wine_analysis_hplc_uv.etl.post_build_library import (
    generic,
    etl_pipeline,
)

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

        if not generic.tbl_exists(
            self.con, tbl_name=self.input_tblname, tbl_type="either"
        ):
            raise AttributeError((f"{self.input_tblname=} not in db"))

        # check if output table name in db, if overwrite is false, raise error, otherwise give warning
        if generic.tbl_exists(self.con, tbl_name=self.output_tblname):
            if not self.overwrite:
                raise ValueError(
                    f"{self.output_tblname} already in db and {self.overwrite=}"
                )
            else:
                warnings.warn(
                    f"{self.output_tblname} already in db and {self.overwrite=}"
                )

        interm_tblname = self._interm_transforms()

        new_tblname = create_table_from_subquery(
            con=self.con,
            new_tblname=self.output_tblname,
            subquery=f"SELECT * FROM {interm_tblname}",
            overwrite=self.overwrite,
            write_to_db=self.write_to_db,
        )

        return new_tblname

    def _interm_transforms(self) -> str:
        """
        Key function unpivoting "chromatogram_spectra".

        :param con: connection object to the database
        :type con: DuckDBPyConnection

        :param input_tbl_name: the name of the input table, the wide table that needs converting to long-form. Defaults to 'chromatogram_spectra'

        :param new_name_suffix: Optional. A string to add to the end of the NEW table name if desired. Defaults to nothing. The table name has the template: '{input_tbl_name}_long_{new_name_suffix}'
        :type new_name_suffix: str

        :return: a polars dataframe containing the unpivoted data, and a string containing the new table name.
        """
        logging.debug(f"unpivoting {self.input_tblname}..")
        # unpivot
        unpivot_tbl = self.con.sql(  # noqa: F841
            f"""--sql
            UNPIVOT
                {self.input_tblname}
            ON
                columns(* exclude(id, mins))
            INTO
                NAME wavelength
                VALUE absorbance
            """
        )  # fmt: skip

        # split wavelength colunn and remove unit prefix

        logging.debug(
            f"removing 'nm_' prefix and writing new TEMP table {self._interm_tblname}.."
        )

        self.con.execute(
            f"""--sql
            CREATE TEMP TABLE {self._interm_tblname} AS (
            SELECT
                id, mins, CAST(split_part(wavelength, '_', 2) AS INT) as wavelength, absorbance

            FROM
                unpivot_tbl
            )
            """
        )  # fmt: skip

        return self._interm_tblname

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
        output_tblname: str = "sample_metadata",
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
        self.build_sample_metadata(con=con)
        pass

    def cleanup(self):
        self.con.execute(f"DROP TABLE {self.output_tblname}")

    def build_sample_metadata(
        self,
        con: db.DuckDBPyConnection,
    ) -> None:
        """
        Assemble the full sample metadata table from the base tables

        1. form the join from the most relevant columns from each table
        2. write to table
        """
        # get the full tables as relations

        subset_columns = dict(
            st=["detection", "samplecode", "ct_wine_name"],
            ct=["color", "varietal", "wine"],
            chm=["id", "ch_samplecode", "join_samplecode"],
        )
        # create relations for each table. Column names are injected as string

        table_subsets = dict(
            st=con.sql(
                f"SELECT {', '.join(subset_columns['st'])} FROM {self.tbl_names['sample_tracker']}"
            ).set_alias("st"),
            ct=con.sql(
                f"SELECT {', '.join(subset_columns['ct'])} FROM {self.tbl_names['cellar_tracker']}"
            ).set_alias("ct"),
            chm=con.sql(
                f"SELECT {', '.join(subset_columns['chm'])} FROM {self.tbl_names['chemstation_metadata']}"
            ).set_alias("chm"),
        )

        # 1. inner join st and ct on 'wine'
        st_ct = (
            table_subsets["st"]
            .join(
                table_subsets["ct"], condition="st.ct_wine_name = ct.wine", how="inner"
            )
            .set_alias("st_ct_join")
        )

        # 2. left join chm and st_ct_join

        chm_st_ct = st_ct.join(  # noqa: F841
            table_subsets["chm"],
            condition="chm.join_samplecode=st_ct_join.samplecode",
            how="left",
        ).set_alias("chm_st_ct_join")

        con.sql(
            """--sql
            CREATE TEMP TABLE sample_metadata_temp
            AS (
                SELECT
                    detection, samplecode, color, varietal, wine, id
                FROM
                    chm_st_ct
            )
            """
        )

        # 4. write it to db if 'write_to_db is True

        subquery = "SELECT * FROM sample_metadata_temp"

        try:
            create_table_from_subquery(
                con=con,
                new_tblname=self.output_tblname,
                subquery=subquery,
                overwrite=self.overwrite,
                write_to_db=self.write_to_db,
            )

        except Exception as e:
            raise e

        return None


def create_table_from_subquery(
    con: db.DuckDBPyConnection,
    new_tblname: str,
    subquery: str,
    overwrite: bool = False,
    write_to_db: bool = False,
) -> str:
    """
    :return: newly written table name
    """
    overwriting = False
    if overwrite and generic.tbl_exists(
        con=con, tbl_name=new_tblname, tbl_type="either"
    ):
        logger.debug(f"overwrite selected but {new_tblname=} not present in db..")
        overwriting = True

    try:
        logger.debug(
            f"{'over' if overwriting else ''}writing {new_tblname=} as {'BASE' if write_to_db else 'TEMPORARY'} table.."
        )
        query = f"CREATE {'OR REPLACE' if overwriting else ''} {'TEMP' if not write_to_db else ''} TABLE {new_tblname} AS ({subquery})"
        con.execute(query)
    except Exception as e:
        raise e

    return new_tblname
