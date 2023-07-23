"""
Write the 'super_table' to excel.
"""

import pandas as pd
import duckdb as db
from wine_analysis_hplc_uv import definitions

from wine_analysis_hplc_uv.definitions import (
    DB_PATH,
    CLEAN_ST_TBL_NAME,
    CLEAN_CT_TBL_NAME,
    CLEAN_CH_META_TBL_NAME,
)
from wine_analysis_hplc_uv.core.super_table_pipe import cellartracker_fuzzy_join

with db.connect(DB_PATH) as con:
    st_rel = con.sql(f"SELECT vintage, name FROM {CLEAN_ST_TBL_NAME}")
    ct_rel = con.sql(f"SELECT vintage, name FROM {CLEAN_CT_TBL_NAME}")

    st_rel.intersect(ct_rel).show()

# get st, ct tables as dfs
with db.connect(DB_PATH) as con:
    st_rel = con.sql(f"SELECT * FROM {CLEAN_ST_TBL_NAME}", alias="st_rel")
    ct_rel = con.sql(f"SELECT * FROM {CLEAN_CT_TBL_NAME}", alias="ct_rel")
    st_df = st_rel.df()
    ct_df = ct_rel.df()
    ch_m_rel = con.sql(f"SELECT * FROM {CLEAN_CH_META_TBL_NAME}", alias="ch_m_rel")

    # join the st, ct in memory with fuzzy search methods
    df = cellartracker_fuzzy_join.cellar_tracker_fuzzy_join(st_df, ct_df)

    # write st-ct join tbl to db
    con.sql("CREATE OR REPLACE TABLE ct_st_join AS SELECT * FROM df")

    # get st-ct join tbl as relation object
    st_ct_join_rel = con.sql("SELECT * FROM ct_st_join", alias="st_ct_join_rel")

    # join ch-m, st-ct tbls as rel objects
    ch_m_st_ct_join_rel = ch_m_rel.join(
        st_ct_join_rel, "ch_m_rel.join_samplecode=st_ct_join_rel.samplecode"
    )

    # drop superf columns

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
        "join_key_similarity",
    ]

    def drop_column(in_rel, column_to_drop):
        # remove specified columns from the freshly formed super-tbl.
        col_set = set(in_rel.columns)
        drop_set = set(column_to_drop)

        select_cols = list(col_set - drop_set)
        out_rel = in_rel.project(",".join(f"'{x}'" for x in select_cols))

        assert len(in_rel.columns) > len(out_rel.columns), "column drop didnt work"
        return out_rel

    super_tbl = drop_column(ch_m_st_ct_join_rel, dropcols)

    # write super-tbl to db
    super_tbl.to_table(definitions.SUPER_TBL_NAME)

#     # write super-tbl to excel
#     import os

#     excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "df.xlsx")

#     (ch_m_st_ct_join_rel.to_df()
#      .drop(dropcols, axis=1)
#      .to_excel(excel_path)
# )
