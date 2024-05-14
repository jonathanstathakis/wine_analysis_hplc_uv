"""
Contains a tool to compare SQL tables using `data_diff`.

As of 2024-05-13 12:35:07 this is not in use as `data_diff` has been dropped as use is too complex, instead use
polars testing suite.
"""

import warnings
from typing import Literal

import data_diff
from data_diff.diff_tables import DiffResultWrapper

warnings.warn("this module is depreceated", DeprecationWarning, stacklevel=2)


def diff_duckdb_tbls_same_db(db_path: str, tbl1: str, tbl2: str):
    """
    generate a DiffTables object for two duckdb tables in the same database
    """
    assert isinstance(db_path, str)
    assert isinstance(tbl1, str)
    assert isinstance(tbl2, str)

    con_str = f"duckdb://{db_path}"

    differ = DiffTables(
        table_1={"con_str": con_str, "name": tbl1},
        table_2={"con_str": con_str, "name": tbl2},
    )
    return differ


def diff_duckdb_tbls_diff_db(
    db_path_1: str,
    db_path_2: str,
    tbl1: str,
    tbl2: str,
    id_col_1: str,
    id_col_2: str,
):
    """
    Generate a DiffTables object based on the input of two tables in different duckdb databases
    """
    assert isinstance(db_path_1, str)
    assert isinstance(db_path_2, str)
    assert isinstance(tbl1, str)
    assert isinstance(tbl2, str)

    con_str_1 = f"duckdb://{db_path_1}"
    con_str_2 = f"duckdb://{db_path_2}"

    differ = DiffTables(
        table_1={"con_str": con_str_1, "name": tbl1, "key_cols": id_col_1},
        table_2={"con_str": con_str_2, "name": tbl2, "key_cols": id_col_2},
    )

    return differ


class DiffTables:
    def __init__(
        self,
        table_1: dict[str, str],
        table_2: dict[str, str],
    ):
        # check table info keys

        expected_keys = ["con_str", "name", "key_cols"]
        for idx, table_info in enumerate([table_1, table_2]):
            if sorted(table_info) != sorted(expected_keys):
                raise ValueError(
                    f"expect input table_info to contain {expected_keys}, got {table_info}"
                )
            # check values are strings
            for key, val in table_info.items():
                if not isinstance(val, str):
                    raise TypeError(
                        f"expect the values of the table dicts to be strings, but table_{idx}, {key}: {type(val)}"
                    )

        # store the validated table info dicts
        self.table_1 = table_1
        self.table_2 = table_2

        # get the diff object
        self._diff = self._find_table_differences()

    def _find_table_differences(self) -> DiffResultWrapper:
        """
        Generate `data_diff.DiffResultWrapper`, an object containing the differences between two tables
        """

        # generate the table objects

        tbl1 = data_diff.connect_to_table(
            db_info=self.table_1["con_str"],
            table_name=self.table_1["name"],
            key_columns=self.table_1["key_cols"],
        )
        tbl2 = data_diff.connect_to_table(
            self.table_2["con_str"],
            table_name=self.table_2["name"],
            key_columns=self.table_2["key_cols"],
        )

        # generate the difference    diff = data_diff.diff_tables(table1=tbl1, table2=tbl2)
        diff = data_diff.diff_tables(tbl1, tbl2)

        assert isinstance(diff, DiffResultWrapper)

        return diff

    def get_diff_stats(self):
        try:
            return self._diff.get_stats_dict()
        except ValueError as e:
            warnings.warn(str(e))
            return None

    def tables_are_different(self) -> bool:
        """
        Return True if the tables are different, else False
        """
        assert True
        return len(list(self._diff)) > 0
