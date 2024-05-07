from wine_analysis_hplc_uv.core.super_table_pipe import cellartracker_fuzzy_join as fj
import logging

logger = logging.getLogger(__name__)


class FormForeignKeySTCT:
    def __init__(self, st_df, ct_df):
        self.st_df = st_df
        self.ct_df = ct_df

    def get_fuzzy_join_df(self):
        logger.info("forming fuzzy join between st and ct..")
        self.join_df = fj.cellar_tracker_fuzzy_join(self.st_df, self.ct_df)
        return self.join_df

    def st_with_foreign_key(self, con):
        """
        join the 'join_df' back to sample_tracker_df by rejoining on left = (vintage, " ", name) and right = (vintage_st + " " + name_st) then drop all but ct_wine
        """
        logger.info("joining st and fuzzy join tbl to add ct wine foreign key to st..")
        join_df = self.get_fuzzy_join_df()

        c_st = con.sql("SELECT * FROM c_sample_tracker").df()

        new_st = con.sql(
            """--sql
            CREATE OR REPLACE TABLE c_sample_tracker
            AS
            SELECT
            st.detection, st.sampler, st.samplecode, st.vintage, st.name, st.open_date, st.sampled_date, st.added_to_cellartracker, st.notes, st.size, CONCAT(join_df.vintage_ct, ' ' , join_df.name_ct) AS ct_wine_name
            FROM
            c_sample_tracker st
            LEFT JOIN
            join_df
            ON
            (CONCAT(st.samplecode,st.vintage, st.name)=CONCAT(join_df.samplecode,join_df.vintage_st,join_df.name_st));
            SELECT * FROM c_sample_tracker
            """
        ).df()

        # check if any nulls
        for col in new_st.columns:
            assert new_st[col].isna().sum() == 0
