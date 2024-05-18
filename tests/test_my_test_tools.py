from pathlib import Path

import duckdb as db
import polars as pl
from polars import testing as pl_test
from tests.my_test_tools import duckdb_tools
from tests.my_test_tools import compare_tables
from tests.my_test_tools.dataset_generation import create_bl_test_set
import pytest


pytest.skip(allow_module_level=True, reason="subjects of tests have been depreceated..")


@pytest.mark.skip
def test_find_table_differences():
    """
    Test `tools.compare_tables.find_table_difference`

    case 1. two tables the same, expect an empty difference list
    case 2. two tables different, expect a filled difference list

    2024-05-13 13:26:19: Dont think this works, not going to try atm.
    """

    table_1_name = "tbl1"
    table_2_name = "tbl2"
    dbpath = Path(__file__).parent / "test_find_diff.db"
    # relpath = Path(dbpath.parent.name) / dbpath.name
    CON_STR = f"duckdb://{str(dbpath)}"

    # need to close the con for data-diff to work, otherwise throws AssertionError when it tries to connect

    with db.connect(str(dbpath)) as con:
        df1 = pl.DataFrame({"id": [0, 2, 3, 4, 5], "b": ["b", "b", "c", "d", "e"]})
        df2 = pl.DataFrame({"id": [1, 2, 3, 4, 5], "b": ["a", "b", "c", "d", "e"]})

        con.sql(f"CREATE OR REPLACE TABLE {table_2_name} AS SELECT * FROM df2")
        con.sql(f"CREATE OR REPLACE TABLE {table_1_name} AS SELECT * FROM df1")

    # case 1
    table_differ_1 = compare_tables.DiffTables(
        table_1={"con_str": CON_STR, "name": table_1_name},
        table_2={"con_str": CON_STR, "name": table_1_name},
    )

    assert not table_differ_1.tables_are_different()

    # case 2, different tables

    table_differ_2 = compare_tables.DiffTables(
        table_1={"con_str": CON_STR, "name": table_1_name},
        table_2={"con_str": CON_STR, "name": table_2_name},
    )

    assert table_differ_2.tables_are_different()


def test_copy_tables_to_other_db():
    """
    test if `copy_tables_to_other_db` works by creating source and destination databases,
    loading the source database with two tables, copying them to the destination database,
    and asserting that the tables are present there. finally, cleanup by deleting the databases
    """

    # assemble the database paths relative to this test module

    # get the cwd of this test module

    cwd = Path(__file__).parent

    # source db

    source_db_filename = Path("source.db")
    source_db_filepath = cwd / source_db_filename

    # destination db

    destination_db_filename = Path("destination.db")
    destination_db_filepath = cwd / destination_db_filename

    # create the tables

    df1 = pl.DataFrame({"a": [1, 2, 3], "b": ["alpha", "beta", "gamma"]})
    df2 = pl.DataFrame({"roderer": [1, 2, 3], "rabbit": ["alpha", "beta", "zeta"]})

    tbl1_name = "tbl1"
    tbl2_name = "tbl2"

    try:
        # create both databases
        source_con = db.connect(str(source_db_filepath))

        ## close destination db con to avoid connection problems during attach
        db.connect(str(destination_db_filepath)).close()

        # load the source database with the tables

        source_con.sql(f"CREATE TABLE {tbl1_name} as SELECT * FROM df1")
        source_con.sql(f"CREATE TABLE {tbl2_name} as SELECT * FROM df2")

        # call the function

        duckdb_tools.copy_tables_across_databases(
            main_con=source_con,
            output_db_path=str(destination_db_filepath),
            tbl_names=[tbl1_name, tbl2_name],
            output_db_alias="output_db",
        )

        dest_con = db.connect(str(destination_db_filepath))

        # compare the tables across the dbs
        for tbl in [
            tbl1_name,
            tbl2_name,
        ]:
            df1 = source_con.sql(f"SELECT * FROM {tbl}").pl()
            df2 = dest_con.sql(f"SELECT * FROM {tbl}").pl()

            pl_test.assert_frame_equal(left=df1, right=df2)

    except Exception as e:
        raise e

    finally:
        # clean up by deleting the database files

        source_db_filepath.unlink()
        destination_db_filepath.unlink()


def test_create_bl_comparison_db(
    output_db_path: str = str(
        Path(Path(__file__).parent, "test_create_bl_compare_db.db")
    ),
):
    try:
        # run the function

        create_bl_test_set.create_comparison_database(
            output_db_path=output_db_path,
        )
    except Exception:
        raise

    finally:
        # cleanup

        Path(output_db_path).unlink()
