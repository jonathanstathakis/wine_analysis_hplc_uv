import duckdb as db
from typing import Self


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
        self.sample_metadata_tblname = sample_metadata_tblname
        self.cs_tblname = cs_tblname
        self.join_key = join_key
        self.sm_sample_tblname = sm_sample_tblname
        self.cs_sample_tblname = cs_sample_tblname
        self.sampling_tbl = "sm_sampling"

    def get_sample_ids(self):
        """
        Get `n` sample ids from the sample metadata table.
        """
        try:
            # first get all non-null id sample entires
            self.non_null_tbl = "sm_non_null_ids"
            self.con.execute(
                f"""--sql
                             CREATE TEMP TABLE {self.non_null_tbl}
                             AS (
                                SELECT
                                    *
                                FROM
                                {self.sample_metadata_tblname}
                                WHERE
                                {self.join_key} IS NOT NULL
                             )
                             """
            )

            # then take a sampling

            self.con.execute(
                f"""--sql
                             
                             CREATE TEMP TABLE {self.sampling_tbl}
                             AS (
                                SELECT
                                    *
                                FROM
                                    {self.non_null_tbl}
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
                        {self.sampling_tbl}

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
        import sqlparse

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
            input_tblname=self.sample_metadata_tblname,
            output_tblname=self.sm_sample_tblname,
            colname=self.join_key,
        )

    def _gen_temp_cs(self):
        """
        Generate the sampling of the chromato-spectral images
        """
        self._gen_temp_sample_table(
            input_tblname=self.cs_tblname,
            output_tblname=self.cs_sample_tblname,
            colname=self.join_key,
        )

    def gen_samples(self):
        """
        Generate sample metadata (`sample_metadata_sample_tblname`) and chromato-spectral image (`cs_sample_tblname`) temporary tables in the input `con` database with the given names.
        """
        try:
            self.get_sample_ids()
            self._gen_temp_sample_metadata()
            self._gen_temp_cs()
        except Exception as e:
            raise e

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

        for tbl in [self.sm_sample_tblname, self.cs_sample_tblname]:
            self._drop_table(tblname=tbl)


class GenSampleCSWide:
    def __init__(
        self,
        con: db.DuckDBPyConnection,
        input_tblname: str = "chromatogram_spectra",
        output_tblname: str = "cs_sample_wide",
        n: int = 5,
    ):
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
