"""
- [x] test logger
- [x] get table into memory as df
- [x] apply cleaner
- [x] test cleaner results
"""
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from tests import test_logger
from tests.mytestmethods.mytestmethods import test_report

from wine_analysis_hplc_uv.cellartracker_methods import cellartracker_cleaner as cleaner
from wine_analysis_hplc_uv.definitions import DB_DIR
import duckdb as db
import os
import pandas as pd


def get_test_db_path():
    return os.path.join(os.getcwd(), "test_clean_ct.db")


def get_db_tbl_as_df(db_path: str, tbl_name: str):
    df = None
    with db.connect(db_path) as con:
        df = con.sql(f"SELECT * FROM {tbl_name}").df()
    return df


def clean_cellartracker_tests(df: pd.DataFrame):
    tests = [
        (test_df_init, df),
        (test_cleaner, df),
    ]

    test_report(tests)
    return None


def test_df_init(df: pd.DataFrame):
    assert isinstance(df, pd.DataFrame)


def test_cleaner(df: pd.DataFrame):
    c_df = cleaner.cellartracker_df_cleaner(df)
    # test if there has been any change at all
    assert not df.equals(c_df)
    # the cleaners first action is to replace 'wine' colname with 'name'
    assert "wine" not in c_df.columns
    assert "name" in c_df.columns
    # the second action is to replace "1001" with np.nan. This is not a very specific function, but I know that it's acting on the vintage col.

    # confirm that 1001 is in the original df
    assert df["Vintage"].isin(["1001"]).any()

    # confirm that 1001 is not in the new df
    assert not c_df["vintage"].isin(["1001"]).any()

    # get the indexes of 1001 in vintage, and the indexes of the new np.nan and confirm that they are equal.

    index_1001 = df[df["Vintage"] == "1001"].index
    index_nan = c_df[c_df["vintage"].isna()].index

    print(index_1001, index_nan)
    assert index_1001.equals(index_nan)


def main():
    tbl_name = "cellar_tracker"
    db_path = DB_DIR
    print(db_path)
    df = get_db_tbl_as_df(db_path=db_path, tbl_name=tbl_name)
    clean_cellartracker_tests(df)


if __name__ == "__main__":
    main()
