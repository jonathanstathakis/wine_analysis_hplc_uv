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


class DataExtractor:
    def __init__(self, db_path: str):
        self.db_path_: str = db_path
        self.con_ = db.connect(db_path)
        self.table_name_: str = "temp_view"

    def create_subset_table(
        self,
        detection: tuple = (None,),
        samplecode: tuple = (None,),
        exclude_samplecodes: tuple = (None,),
        color: tuple = (None,),
        wavelengths: int | list | tuple = None,
        varietal: tuple = (None,),
        wine: tuple = (None,),
        mins: tuple = (None, None),
    ):
        cs_cols = self.con_.execute(
            """--sql
                                    SELECT
                                        column_name
                                    FROM
                                        duckdb_columns()
                                    WHERE
                                        table_name='chromatogram_spectra'
                                        AND
                                        REGEXP_MATCHES(column_name, '^nm_[0-9]+$')
                                    """
        ).df()

        cs_col_list = self.select_wavelengths(cs_cols, wavelengths)

        # Join the data tables together

        self.con_.execute(
            query=f"""--sql
                    CREATE OR REPLACE TEMPORARY TABLE {self.table_name_} AS
                    (
                        SELECT
                                st.detection,
                                ct.color,
                                ct.varietal,
                                chm.id,
                                CONCAT_WS('_',st.samplecode, ct.wine) AS code_wine,
                                cs.mins,
                                {cs_col_list}
                        FROM
                        c_sample_tracker st
                        INNER JOIN
                            c_cellar_tracker ct ON st.ct_wine_name = ct.wine
                        LEFT JOIN
                            c_chemstation_metadata chm ON
                                (
                                chm.join_samplecode=st.samplecode
                                )
                        LEFT JOIN
                            chromatogram_spectra cs ON (chm.id=cs.id)
                    
                        WHERE
                            (
                                (SELECT UNNEST($detection)) IS NULL
                                OR st.detection IN (SELECT * FROM UNNEST($detection))
                            )
                        AND (
                                (SELECT UNNEST($samplecode)) IS NULL
                                OR st.samplecode IN (SELECT * FROM UNNEST($samplecode))
                             )
                        AND
                        (
                            (SELECT UNNEST($color)) IS NULL
                              OR ct.color IN (SELECT * FROM UNNEST($color))
                              )
                            AND ((SELECT UNNEST($varietal)) IS NULL
                              OR ct.varietal IN (SELECT * FROM UNNEST($varietal)))
                            AND ((SELECT UNNEST($wine)) IS NULL
                              OR ct.wine IN (SELECT * FROM UNNEST($wine)))
                            AND ($min_start IS NULL OR cs.mins >= $min_start)
                            AND ($min_end IS NULL OR cs.mins <= $min_end)
                            AND ((SELECT UNNEST($exclude_samplecodes)) IS NULL
                              OR st.samplecode NOT IN (SELECT * FROM UNNEST($exclude_samplecodes))
                            )
                    )
                            """,
            parameters={
                "detection": detection,
                "samplecode": samplecode,
                "exclude_samplecodes": exclude_samplecodes,
                "color": color,
                "varietal": varietal,
                "wine": wine,
                "min_start": mins[0],
                "min_end": mins[1],
            },
        )

        self.con_.sql(
            f"""--sql
        SELECT * FROM {self.table_name_}
        """
        )

    def get_tbl_as_df(self):
        return self.con_.sql(
            f"""--sql
                             SELECT * FROM {self.table_name_}
                             """
        ).df()

    def select_wavelengths(self, columns, wavelengths: str | list):
        columns = (
            columns["column_name"]
            .str.split("_", expand=True)
            .set_axis(axis=1, labels=["unit", "wavelength"])
            .assign(wavelength=lambda df: df["wavelength"].astype(int))
        )

        if isinstance(wavelengths, (list, tuple)):
            columns = columns.query("wavelength in @wavelengths")

        elif wavelengths == "all":
            columns = columns

        elif isinstance(wavelengths, int):
            columns = columns.query("wavelength==@wavelengths")

        else:
            raise ValueError(
                f"expecting list or tuple or string or None for wavelengths, got{type(wavelengths)}"
            )

        columns = columns.assign(
            tbl_wavelength_strs=columns.loc[:, "unit"]
            + "_"
            + columns.loc[:, "wavelength"].astype(str)
        )

        # turn them into a sql friendly list
        cs_col_list = ", ".join([f"cs.{col}" for col in columns["tbl_wavelength_strs"]])

        return cs_col_list


class RawTestSet3DCreator(DataExtractor):
    """
    Class to replicate the RAW3DSET parquet file
    """

    def __init__(self, db_path: str):
        DataExtractor.__init__(self, db_path=db_path)

        self.create_subset_table(
            wavelengths=list(range(190, 402, 2)),
            detection=("raw",),
            exclude_samplecodes=("72", "98"),
        )

        self.df = self.get_tbl_as_df().dropna()


def main():
    db_path = definitions.DB_PATH

    rtsc = RawTestSet3DCreator(db_path)


if __name__ == "__main__":
    main()
