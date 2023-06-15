"""
Compare the contents of base chemstation metadata table with sample tracker table to identify what cleaning needs to be done to form a union.
"""
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.definitions import DB_PATH, CH_META_TBL_NAME, ST_TBL_NAME
import pandas as pd


def compare_columns(col1, col2):
    comparison = col2[~(col2.isin(col1))]
    print(comparison)
    print(comparison.shape)


def main():
    st_df = db_methods.tbl_to_df(db_filepath=DB_PATH, tblname=ST_TBL_NAME)
    ch_m_df = db_methods.tbl_to_df(db_filepath=DB_PATH, tblname=CH_META_TBL_NAME)
    ch_m_df = ch_m_df.rename({"notebook": "id"}, axis=1)
    compare_columns(col1=st_df["id"], col2=ch_m_df["id"])


if __name__ == "__main__":
    main()
