""" """

import logging
import duckdb as db

logger = logging.getLogger(__name__)


def copy_tables_across_databases(
    main_con: db.DuckDBPyConnection,
    output_db_path: str,
    tbl_names: str | list[str],
    summarize: bool = False,
    output_db_alias: str = "output_db",
) -> list[str]:
    """
    TODO: test this

    Write `tbl_names` in `main_con` to a dataase at `output_db_path`, signified as `output_db_name` in the main database.

    :param main_con: a connection object to the source object
    :type main_con: db.DuckDBPyConnection
    :param output_db_path: a local filepath to the destination database.
    :type output_db_path: str
    :param tbl_names: a list of names of tables to copy to the destination database
    :type tbl_names: str | list[str]
    :param summarize: Whether to write the full table of a duckdb summary, refer to the SUMMARIZE docs for more information, defaults to False
    :type summarize: bool, optional
    :param output_db_name: The alias to refer to the destination database in the source database, relevent for downstream queries, defaults to "output_db"
    :type output_db_name: str, optional
    :raises ValueError: If there is a problem in the copy query
    :return: the list of tables added to the destination database, should be equal to `tbl_names`
    :rtype: list[str]
    """

    # regularise input

    if isinstance(tbl_names, str):
        input_tblnames = [tbl_names]
    else:
        input_tblnames = tbl_names

    # get all table names currently in the output database
    with db.connect(output_db_path) as output_con:
        curr_tbl_names_in_output_db = get_tbl_names(con=output_con)

    # attach the output db to the main db

    sub_db_name = attach_db(
        main_con=main_con,
        subordinate_db_path=output_db_path,
        subordinate_db_name=output_db_alias,
    )

    # iterate through the table names, generate the summaries and write them to the summaries db

    for tbl in input_tblnames:
        if summarize:
            main_con.sql(f"SUMMARIZE {tbl}")
        else:
            main_con.sql(f"FROM {tbl}")

        main_con.sql(
            f"CREATE TABLE {output_db_alias}.{str(tbl)} AS SELECT * FROM output_tbl"
        )

    # detach the dbs
    detach_db(main_con=main_con, subordinate_db_name=sub_db_name)

    # validate the process by comparing the tables in the output db before and after write

    ## get all the table names in the database after write

    if table_names_after_result := main_con.sql(
        "SELECT table_name FROM duckdb_tables"
    ).fetchall():
        table_names_after = [result[0] for result in table_names_after_result]

    else:
        raise ValueError("Failed to create any tables in database")

    # if there were tables in the db before writing the new tables
    if curr_tbl_names_in_output_db:
        newly_created_tbl_names = [
            tbl_name
            for tbl_name in table_names_after not in curr_tbl_names_in_output_db
        ]
    else:
        newly_created_tbl_names = table_names_after

    logger.debug(
        f"added the following tables to the summary database: {newly_created_tbl_names}"
    )

    return newly_created_tbl_names


def get_tbl_names(con: db.DuckDBPyConnection) -> list[str]:
    """
    retrieve the table names present in the database represented through `con`. If no table names are retrieved, returns an empty list

    :param con: connection to the target database
    :type con: db.DuckDBPyConnection
    :return: list of tables in databaes
    :rtype: str[list]
    """
    if tbl_name_results := con.sql("SELECT table_name from duckdb_tables").fetchall():
        curr_tbl_names = [result[0] for result in tbl_name_results]
    else:
        return []
    return curr_tbl_names


def attach_db(
    main_con: db.DuckDBPyConnection,
    subordinate_db_path: str,
    subordinate_db_name: str,
) -> str:
    """
    Attach a subordinate database to a main database represented as `main_con`

    :param main_con: connection to the main database
    :type main_con: db.DuckDBPyConnection
    :param subordinate_db_path: path to the subordinate database to be connected
    :type subordinate_db_path: str
    :param subordinate_db_name: name to use to represen the subordinate database in the main database, for prefixing identifiers in queries. Useful for downstream queries, defaults to 'sub_db'
    :type subordinate_db_name: str, optional
    :return: the subordinate_db_name
    :rtype: str
    """
    # connect the new db to the current session
    logger.debug(f"attaching {subordinate_db_name} to input db")

    main_con.sql(f"ATTACH '{subordinate_db_path}' AS {subordinate_db_name}")

    return subordinate_db_name


def detach_db(
    main_con: db.DuckDBPyConnection,
    subordinate_db_name: str,
) -> None:
    """
    Detach an attached subordinate db from a main database


    :param main_con: connection object to the main database, the database to be detached from
    :type main_con: db.DuckDBPyConnection
    :param subordinate_db_name: the alias of the attached database in the main database
    :type subordinate_db_name: str
    """
    logger.debug(f"detaching {subordinate_db_name}..")
    main_con.sql(f"DETACH {subordinate_db_name}")
    logger.debug(f"detached {subordinate_db_name}..")
