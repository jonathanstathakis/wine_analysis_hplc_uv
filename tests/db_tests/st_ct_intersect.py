import pandas as pd
import duckdb as db

from wine_analysis_hplc_uv.definitions import (
    DB_PATH,
    CLEAN_ST_TBL_NAME,
    CLEAN_CT_TBL_NAME,
    CLEAN_CH_META_TBL_NAME,
)
from wine_analysis_hplc_uv.core.super_table_pipe import cellartracker_fuzzy_join

# currently there is only an intersection of 47 rows out of 190 in sampletracker. Need to use the fuzzy join function
with db.connect(DB_PATH) as con:
    st_rel = con.sql(f"SELECT vintage, name FROM {CLEAN_ST_TBL_NAME}")
    ct_rel = con.sql(f"SELECT vintage, name FROM {CLEAN_CT_TBL_NAME}")

    st_rel.intersect(ct_rel).show()

with db.connect(DB_PATH) as con:
    st_rel = con.sql(f"SELECT * FROM {CLEAN_ST_TBL_NAME}", alias="st_rel")
    ct_rel = con.sql(f"SELECT * FROM {CLEAN_CT_TBL_NAME}", alias="ct_rel")
    st_df = st_rel.df()
    ct_df = ct_rel.df()
    ch_m_rel = con.sql(f"SELECT * FROM {CLEAN_CH_META_TBL_NAME}", alias="ch_m_rel")

    df = cellartracker_fuzzy_join.cellar_tracker_fuzzy_join(st_df, ct_df)
    con.sql("CREATE OR REPLACE TABLE ct_st_join AS SELECT * FROM df")
    st_ct_join_rel = con.sql("SELECT * FROM ct_st_join", alias="st_ct_join_rel")

    ch_m_st_ct_join_rel = ch_m_rel.join(
        st_ct_join_rel, "ch_m_rel.join_samplecode=st_ct_join_rel.samplecode"
    )
    import os

    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "df.xlsx")
    dropcols = [
        "name_st",
        "vintage_st",
        "vialnum",
        "originalfilepath",
        "join_samplecode",
        "added_to_cellartracker",
        "size_st",
        "sequence",
        "join_key_st",
        "join_key_ct",
        "join_key_matched",
    ]
    ch_m_st_ct_join_rel.to_df().drop(dropcols, axis=1).to_excel(excel_path)
