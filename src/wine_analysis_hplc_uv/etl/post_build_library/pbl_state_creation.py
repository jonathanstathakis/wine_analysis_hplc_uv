"""
move the library state forward by running a series of sql queries

TODO: set up the state
TODO: run the queries
TODO: verify the outcome
"""
# TODO: establish the main function

from wine_analysis_hplc_uv import definitions
import duckdb as db
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def create_pbl_schema():
    return get_query_str(form_filepaths("create_pbl_schema.sql"))


def pbl_cs_long_as_cte():
    return get_query_str(form_filepaths("create_cs_long.sql"))


def sample_metadata_create_as_cte():
    return get_query_str(form_filepaths("create_sample_metadata.sql"))


def update_library(con: db.DuckDBPyConnection, schema_name="pbl"):
    """
    Main. load the queries as strings and execute them.

    if testing is needed, wrap this in a transaction. it does not contain any error handling.
    """

    query_paths = get_sql_script_filepaths()
    queries = get_input_queries(query_paths)

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


def get_input_queries(path_dict: dict[str, str]) -> dict[str, str]:
    """
    for a dict of names: filepaths, read the contents of the files and return as strings in a dict whose keys are the names of the input dict. raises an error if any paths dont exist
    """

    return {
        name: get_query_str(path)
        for name, path in path_dict.items()
        if Path(path).exists()
    }


def get_sql_script_filepaths() -> dict:
    """
    return a dict of filepaths to each of the sql scripts. keys are names of the script, value is the path
    """

    filenames = [
        "add_indexes.sql",
        "create_pbl_schema.sql",
        "create_sample_metadata.sql",
        "create_cs_long.sql",
    ]

    return {name.replace(".sql", ""): form_filepaths(name) for name in filenames}


def form_filepaths(file_name: str) -> str:
    """
    return query filepaths in the pbl directory by concatenating them with the stored directory path
    """
    path = str(Path(definitions.PBL) / file_name)
    assert Path(path).exists(), f"{path}"
    return path


def get_query_str(path: str) -> str:
    """
    open input path and return the content
    """
    with open(path, "r") as f:
        return f.read()
