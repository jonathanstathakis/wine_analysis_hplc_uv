"""
Contains the `SampleTableGenerator` which adds temporary samplings of 'sample_metadata' and 'chromatogram_spectra_long' for testing
"""

from typing import Self

import duckdb as db
import sqlparse


class SampleTableGenerator:
    def __init__(
        self,
        con: db.DuckDBPyConnection,
        n: int = 5,
        sample_metadata_tblname: str = "sample_metadata",
        cs_tblname: str = "chromatogram_spectra_long",
        join_key: str = "id",
        sm_sample_tblname: str = "sample_metadata_sample",
        cs_sample_tblname: str = "cs_sample",
    ):
        """
        For a given `input_tblname` retrieve `n` sample ids. Use to construct a random sampleset
        for testing.

        To reduce scenario complexity, we need all ids to be present in both tables. Hence, we first get a sampling
        of sample ids then create temporary tables of both metadata and chromato-spectral images from those
        ids. Thus any nulls are a red flag.
        """

        self.con = con
        self.n = n
        self.tblnames = {}
        self.join_key = join_key

        self.sample_ids = None

        self.intm_sm_tblnames = dict(sampling="sm_sampling", non_null="sm_non_null_ids")

        self.tblnames = dict(
            sm=sample_metadata_tblname,
            cs=cs_tblname,
            sm_sample=sm_sample_tblname,
            cs_sample=cs_sample_tblname,
        )

    def get_sample_ids(self):
        """
        Get `n` sample ids from the sample metadata table.
        """
        try:
            # first get all non-null id sample entires
            self.con.execute(
                f"""--sql
                             CREATE TEMP TABLE {self.intm_sm_tblnames['non_null']}
                             AS (
                                SELECT
                                    *
                                FROM
                                {self.tblnames['sm']}
                                WHERE
                                {self.join_key} IS NOT NULL
                             )
                             """
            )

            # then take a sampling

            self.con.execute(
                f"""--sql
                             
                             CREATE TEMP TABLE {self.intm_sm_tblnames['sampling']}
                             AS (
                                SELECT
                                    *
                                FROM
                                    {self.intm_sm_tblnames['non_null']}
                                USING
                                    SAMPLE {self.n}
                                
                             )


            """
            )

            # finally select only the ids as a flat tuple

            ids = self.con.execute(
                f"""--sql
                    SELECT distinct({self.join_key})
                    FROM
                        {self.intm_sm_tblnames['sampling']}

                    """
            ).fetchall()

            self.sample_ids = tuple(val[0] for val in ids)

            if any(id for id in self.sample_ids if id is None):
                raise ValueError("Null id value returned")
        except ValueError as e:
            e.add_note("need to implement an identification of null value id samples")
            raise e

        return ids

    def _gen_temp_sample_table(
        self, input_tblname: str, output_tblname: str, colname: str
    ):
        """
        Given the previously generated `n` ids, create a session-specific temporary
        sample table
        """

        if not self.sample_ids:
            raise RuntimeError(
                "no sample ids collected, ensure to run `get_sample_ids`"
            )

        query = sqlparse.format(
            f"""--sql
                            CREATE TEMP TABLE {output_tblname}
                            AS (
                            SELECT
                                *
                            FROM
                                {input_tblname}
                            WHERE
                                {colname} IN {self.sample_ids}
                            )
            """,
            keyword_case="upper",
            reindent=True,
        )
        try:
            self.con.execute(query)
        except db.ParserException as e:
            e.add_note(f"submitted query:\n\n{query}")
            raise e

    def _gen_temp_sample_metadata(self):
        """
        Generate the sampling of the sample metadata
        """

        self._gen_temp_sample_table(
            input_tblname=self.tblnames["sm"],
            output_tblname=self.tblnames["sm_sample"],
            colname=self.join_key,
        )

    def _gen_temp_cs(self):
        """
        Generate the sampling of the chromato-spectral images
        """
        self._gen_temp_sample_table(
            input_tblname=self.tblnames["cs"],
            output_tblname=self.tblnames["cs_sample"],
            colname=self.join_key,
        )

    def gen_samples(self) -> Self:
        """
        Generate sample metadata (`sample_metadata_sample_tblname`) and chromato-spectral image (`cs_sample_tblname`) temporary tables in the input `con` database with the given names.
        """
        try:
            self.get_sample_ids()
            self._gen_temp_sample_metadata()
            self._gen_temp_cs()
        except Exception as e:
            raise e

        return self

    def _drop_table(self, tblname: str):
        try:
            self.con.execute(
                f"""--sql
                DROP TABLE {tblname}
            """
            )
        except Exception as e:
            raise e

    def cleanup(self):
        """
        reverse the action of `gen_samples`, if necessary
        """

        for tbl in [self.tblnames["sm_sample"], self.tblnames["cs_sample"]]:
            self._drop_table(tblname=tbl)


class GenSampleCSWide:
    def __init__(
        self,
        con: db.DuckDBPyConnection,
        input_tblname: str = "chromatogram_spectra",
        output_tblname: str = "cs_sample_wide",
        n: int = 5,
    ):
        """
        Use `self.gen_sample_cs_wide` to create a temporary sampling of the wide "chromatogram_spectra" table.
        Used for testing the wide to long transformation.
        """
        self.con = con
        self.output_tblname = output_tblname
        self.input_tblname = input_tblname
        self.n = n

    def gen_sample_cs_wide(self) -> Self:
        self.con.execute(
            f"""--sql
            CREATE TEMP TABLE {self.output_tblname}
            AS (
                SELECT * FROM {self.input_tblname}
                WHERE id IN (
                SELECT
                    DISTINCT(id) FROM {self.input_tblname}
                WHERE
                    id IS NOT NULL
                USING
                    SAMPLE {self.n}
                )
            )
            """
        )

        return self
