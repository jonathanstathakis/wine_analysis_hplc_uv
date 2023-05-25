"""

"""
from wine_analysis_hplc_uv.devtools import project_settings, function_timer as ft
import os
import duckdb as db


def maim():
    metadata_table_name = "metadata"
    spectrum_table_name = "spectrums"
    db_filename = "wine_auth_db.db"
    db_filepath = os.path.join(os.getcwd(), db_filename)
    write_db_colnames_to_file(db_filepath, spectrum_table_name)
    write_db_colnames_to_file(db_filepath, table_name)


def write_db_colnames_to_file(db_filepath: str, table_name: str):
    column_names = get_column_names(db_filepath, table_name)
    col_filename = "spectrum_table_colnames.txt"

    write_colnames_to_file(colnames, col_filename)

    return None


def get_column_names(db_filepath, table_name):
    with db.connect(db_filepath) as con:
        result = con.execute(f"PRAGMA table_info({table_name})").fetchdf()
    column_names = result["name"].tolist()
    return column_names


def write_colnames_to_file(colnames: list, col_filename: str) -> None:
    with open(col_filename, "w") as f:
        for line in column_names:
            f.write(line)
            f.write("\n")

    with open(col_filename, "r") as f:
        assert len(f.readlines()) > 0, "file empty"

    return None


if __name__ == "__main__":
    main()
