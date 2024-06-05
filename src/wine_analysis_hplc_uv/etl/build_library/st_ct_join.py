from wine_analysis_hplc_uv.etl.build_library.super_table_pipe import (
    cellartracker_fuzzy_join as fj,
)
import logging
import pandas as pd
import duckdb as db
from wine_analysis_hplc_uv import definitions

logger = logging.getLogger(__name__)


class FormForeignKeySTCT:
    def __init__(self, st_df, ct_df):
        self.st_df = st_df
        self.ct_df = ct_df

    def _get_fuzzy_join_df(self) -> pd.DataFrame:
        logger.info("forming fuzzy join between st and ct..")
        self.join_df = fj.cellar_tracker_fuzzy_join(self.st_df, self.ct_df)
        return self.join_df

    def write_st_with_foreign_key(self, con: db.DuckDBPyConnection) -> str:
        """
        Replace `c_sample_tracker` table in database, but with forein key 'ct_wine_name', enabling joins with cellar tracker table.

        :returns: newly created sample tracker table name
        :type return: str

        ## Redesign

        2024-05-14 11:34:27

        Testing has shown that several wines in the new sample tracker table have no vintage.

        It is not apparent why this is the case, but is presumably a symptom of join keys being present in sample tracker, but not cellar tracker, i.e. a wine has not been added to cellar tracker. It is not worth trying to fix now, and will mark the associated test as xfail. To fix:

        TODO: redesign as a series of sql queries, utilizing duckdb native string similarity metrics.
        TODO: the flow will proceed as follows:
            1. form the join keys
            2. find the similarity
            3. raise a warning about wines with a low similarity score.
            4. add the ct wine names and similarity to sample tracker via UPDATE TABLE
        """
        logger.info("joining st and fuzzy join tbl to add ct wine foreign key to st..")

        self._get_fuzzy_join_df()

        new_tbl = definitions.Clean_tbls.ST

        new_st = con.sql(
            f"""--sql
            -- join the 'join_df' back to sample_tracker_df by rejoining on left = (vintage, " ", name) and right = (vintage_st + " " + name_st) then drop all but ct_wine
            CREATE OR REPLACE TABLE {new_tbl}
            AS (
                SELECT
                    st.detection, st.sampler, st.samplecode, st.vintage, st.name, st.open_date, st.sampled_date, st.added_to_cellartracker, st.notes, st.size, CONCAT(join_df.vintage_ct, ' ' , join_df.name_ct) AS ct_wine_name
                FROM
                    c_sample_tracker st
                LEFT JOIN
                    join_df
                ON
                    (CONCAT(st.samplecode,st.vintage, st.name)=CONCAT(join_df.samplecode,join_df.vintage_st,join_df.name_st))
            );
            SELECT * FROM c_sample_tracker
            """
        ).df()

        # check if any nulls.
        # 2024-05-14 10:54:28. How do nulls occur? As it is a left join, any columns from the right table whose values do not have a join value in the left table will now contain null. Thus, sample_tracker contains rows whose join key has not been matched to one in cellar tracker. Specifically, 15 rows, all the same batch, 2023-05-16.

        # no apparent clues as to why this is happening, try joining the null vintage rows to the base tables
        for col in new_st.columns:
            assert new_st[col].isna().sum() == 0

        return new_tbl
