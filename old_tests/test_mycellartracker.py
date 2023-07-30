"""
testing the new MyCellarTracker class 

- [x] initialise MyCellarTracker class
- [x] MyCellarTracker.df has expected content.
- [ ] MyCellarTracker exports (define as an 'exporter' class):
    - [x] to sheets
    - [x] to db
    - [ ] integration into MyCellarTracke
    
"""
import os
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from tests.mytestmethods.mytestmethods import test_report
from wine_analysis_hplc_uv.df_methods.df_methods import test_df
from wine_analysis_hplc_uv.my_sheetsinterface.gspread_methods import WorkSheet
from wine_analysis_hplc_uv.cellartracker_methods.my_cellartracker_class import (
    MyCellarTracker,
    Exporter,
)


def test_mycellartracker():
    tests = [
        (test_mycellartracker_init,),
        (test_mycellartracker_df,),
        (test_exporter_to_sheets,),
        (test_exporter_to_db,),
        (test_CellarTracker_to_db,),
    ]

    test_report(tests)

    return None


def un():
    un = os.environ.get("CELLAR_TRACKER_UN")
    assert isinstance(un, str)
    return un


def pw():
    pw = os.environ.get("CELLAR_TRACKER_PW")
    assert isinstance(pw, str)
    return pw


def test_mycellartracker_init(username=un(), password=pw()):
    cellartracker = MyCellarTracker(username=username, password=password)
    assert cellartracker
    return None


def test_mycellartracker_df(username=un(), password=pw()):
    cellartracker = MyCellarTracker(username=username, password=password)
    test_df(cellartracker.df)

    assert not cellartracker.df.empty
    return None


def test_exporter_to_sheets(username=un(), password=pw()):
    def get_key():
        return os.environ.get("TEST_SAMPLE_TRACKER_KEY")

    def get_sheet_title():
        return "test_exporter"

    exporter = Exporter()
    exporter.df = MyCellarTracker(username=username, password=password).df

    exporter.to_sheets(get_key(), get_sheet_title())

    wksh = WorkSheet(key=get_key(), sheet_title=get_sheet_title())

    # check that exported df matches the df created from the written sheet
    assert exporter.df.equals(wksh.sheet_df)

    wksh.delete_sheet(wksh.wksh)


def test_exporter_to_db(
    username=un(),
    password=pw(),
    db_filepath="test_exporter.db",
    tbl_name="test_exporter",
):
    exporter = Exporter()
    exporter.df = MyCellarTracker(username=username, password=password).df

    import duckdb as db

    with db.connect(db_filepath) as con:
        con.sql(f"DROP TABLE IF EXISTS {tbl_name}")

    exporter.to_db(db_filepath, tbl_name)

    import pandas as pd

    db_df = pd.DataFrame()
    with db.connect(db_filepath) as con:
        db_df = con.sql(f"SELECT * FROM {tbl_name}").df()

    assert exporter.df.shape == db_df.shape
    assert exporter.df.shape > (0, 0)
    assert db_df.shape > (0, 0)

    print(db_df.head())

    with db.connect(db_filepath) as con:
        con.sql(f"DROP TABLE {tbl_name}")


def test_CellarTracker_to_db(
    username=un(),
    password=pw(),
    db_filepath="test_exporter.db",
    tbl_name="test_exporter",
):
    mycellartracker = MyCellarTracker(username=username, password=password)

    import duckdb as db

    with db.connect(db_filepath) as con:
        con.sql(f"DROP TABLE IF EXISTS {tbl_name}")

    mycellartracker.to_db(db_filepath, tbl_name)

    import pandas as pd

    db_df = pd.DataFrame()
    with db.connect(db_filepath) as con:
        db_df = con.sql(f"SELECT * FROM {tbl_name}").df()

    assert mycellartracker.df.shape == db_df.shape
    assert mycellartracker.df.shape > (0, 0)
    assert db_df.shape > (0, 0)

    print(db_df.head())

    with db.connect(db_filepath) as con:
        con.sql(f"DROP TABLE {tbl_name}")


def main() -> None:
    test_mycellartracker()

    return None


if __name__ == "__main__":
    main()