import duckdb as db
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DBInterface:
    def __init__(self, dbpath: str):
        self._dbpath = dbpath
        self._con = db.connect(self._dbpath)

    def show_tables(self):
        self._con.sql("SHOW TABLES").show()

    def _checkexists(self, tblname: str):
        checkexistquery = f"""--sql
                SELECT
                CASE
                    WHEN EXISTS (SELECT 1 FROM duckdb_tables() WHERE table_name='{tblname}')
                    THEN TRUE
                    ELSE FALSE
                END AS table_exists;
                """

        table_exists = self._con.sql(checkexistquery).fetchall()[0][0]

        return table_exists

    def insert_df_into_tbl(self, df: pd.DataFrame, tblname: str) -> None:
        """
        There are two options: either create a new table or insert into existing. Provide logic for both
        """

        insertquery = f"""--sql
        INSERT INTO {tblname} SELECT * FROM df
        """

        # if table doesnt exist, create table as an insersion of the dataframe

        if not self._checkexists(tblname=tblname):
            logging.info(f"{tblname} not in db, creating from input df..")

            createquery = f"""--sql
            CREATE TABLE IF NOT EXISTS {tblname} AS SELECT * FROM df
            """

            self._con.sql(createquery)

            return None

        # else if table exists, just insert

        else:
            logging.info(f"inserting contents of df into {tblname}..")
            self._con.sql(insertquery)

            return None

    def describe_table(self, tblname) -> None:
        describe_query = f"""--sql
        DESCRIBE {tblname}
        """

        self._con.sql(describe_query).show()
        self._get_rowcount(tblname)

        return None

    def _get_rowcount(self, tblname) -> pd.DataFrame:
        rowcountquery = f"""--sql
        SELECT 'rows' AS rows, COUNT(*) AS numrows FROM {tblname}
        """

        rowcount = self._con.sql(rowcountquery).df()

        return rowcount

    def drop_tbl(self, tblname) -> None:
        """
        delete_tbl remove the target table from the db

        See [Drop Statement](https://duckdb.org/docs/sql/statements/drop.html)


        :param tblname: _description_
        :type tblname: _type_
        """

        deletequery = f"""--sql
        DROP TABLE {tblname}
        """

        self._con.sql(deletequery)

        return None
