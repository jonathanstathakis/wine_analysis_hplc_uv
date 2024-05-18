import sqlparse
import duckdb as db

from typing import Literal


def tbl_exists(
    con: db.DuckDBPyConnection,
    tbl_name: str,
    tbl_type: Literal["base", "temp", "either"] = "base",
):
    """
    check if table present in db. If no table matching `tbl_name` is present, returns False, else True.

    if 'either', table can be base or temp type
    """
    tbl_types = {"base": "BASE TABLE", "temp": "LOCAL TEMPORARY"}

    query = []

    query.append(
        f"SELECT DISTINCT(table_name) FROM information_schema.tables WHERE table_name = '{tbl_name}'"
    )

    if tbl_type == "either":
        query.append(
            f"AND table_type='{tbl_types['base']}' OR table_type='{tbl_types['temp']}'"
        )
    else:
        query.append(f"AND table_type='{tbl_types[tbl_type]}'")

    query_str = " ".join(query)
    tbl_names = con.execute(query_str).pl()

    is_empty = tbl_names.is_empty()

    return not is_empty


class DataBaseInspector:
    def __init__(self, con: db.DuckDBPyConnection):
        """
        Provide basic inspection methods of a given duckdb database through con
        TODO: write tests for this
        """

        self.con = con

    def _format_query(self, query: str):
        """
        format a given query via sqlparse
        """
        formatted_query = sqlparse.format(
            sql=query,
            keyword_case="upper",
            identifier_case="lower",
            reindent=True,
        )

        return formatted_query

    def all_tables_by_type(self):
        query = self._format_query(
            query="""--sql
            SELECT
                table_name, table_type
            FROM
                information_schema.tables
        """
        )

        return self.con.sql(query)

    def get_tbl_by_name(self, tblname: str):
        query = self._format_query(
            query=f"""--sql
            SELECT
                *
            FROM
                {tblname}
            """
        )

        return self.con.sql(query)
