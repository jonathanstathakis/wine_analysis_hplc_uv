"""
Test db_methods
"""
import os

from db_methods import db_methods
from devtools import function_timer as ft
from devtools import project_settings


def test_db_methods():
    db_filepath = os.path.join(os.getcwd(), "wine_auth_db.db")
    table_name = "chemstation_metadata"
    db_methods.test_db_table_exists(db_filepath, table_name)
    return None


def main():
    test_db_methods()
    return None


if __name__ == "__main__":
    main()
