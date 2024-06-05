"""
move the library state forward by running a series of sql queries
"""

from wine_analysis_hplc_uv import definitions
import duckdb as db
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def update_library(con: db.DuckDBPyConnection):
    """
    Main. load the queries as strings and execute them.

    if testing is needed, wrap this in a transaction. it does not contain any error handling.
    """

    query_paths = _get_sql_script_filepaths()
    queries = _get_input_queries(query_paths)

    # create the schema to contain all of the output tables

    try:
        for name, query in queries.items():
            logger.info(f"executing {name}..")
            con.sql(query)
            logger.info(f"finished executing {name}..")

            assert True
    except db.ParserException as e:
        e.add_note(name)
        raise e
    logger.info("done executing queries")


## below 3 functions return the query as a string. Currently only used in a test


def _create_pbl_schema():
    return _get_query_str(_form_filepaths("create_pbl_schema.sql"))


def _pbl_cs_long_as_cte():
    return _get_query_str(_form_filepaths("create_cs_long.sql"))


def _sample_metadata_create_as_cte():
    return _get_query_str(_form_filepaths("create_sample_metadata.sql"))


def _get_input_queries(path_dict: dict[str, str]) -> dict[str, str]:
    """
    for a dict of names: filepaths, read the contents of the files and return as strings in a dict whose keys are the names of the input dict. raises an error if any paths dont exist
    """

    return {
        name: _get_query_str(path)
        for name, path in path_dict.items()
        if Path(path).exists()
    }


def _get_sql_script_filepaths() -> dict:
    """
    return a dict of filepaths to each of the sql scripts. keys are names of the script, value is the path
    """

    filenames = [
        "add_indexes.sql",
        "create_pbl_schema.sql",
        "create_sample_metadata.sql",
        "create_cs_long.sql",
    ]

    return {name.replace(".sql", ""): _form_filepaths(name) for name in filenames}


def _form_filepaths(file_name: str) -> str:
    """
    return query filepaths in the pbl directory by concatenating them with the stored directory path
    """
    path = str(Path(definitions.PBL) / "queries" / file_name)
    assert Path(path).exists(), f"{path}"
    return path


def _get_query_str(path: str) -> str:
    """
    open input path and return the content
    """
    with open(path, "r") as f:
        return f.read()
