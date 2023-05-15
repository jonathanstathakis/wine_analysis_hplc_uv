import pandas as pd
from ..sampletracker import sample_tracker_methods
from ..db_methods import db_methods
import duckdb as db
from ..google_sheets_api import google_sheets_api


def init_raw_sample_tracker_table(db_filepath: str, table_name: str) -> None:
    # download the current sample tracker table
    df = sample_tracker_methods.sample_tracker_df_builder()
    df = df.replace({"": None})
    write_raw_sample_tracker_to_db(df, db_filepath, table_name)
    db_methods.display_table_info(db_filepath, table_name)
    return None


def write_raw_sample_tracker_to_db(df: pd.DataFrame, db_filepath: str, db_table_name: str):
    schema = """
        id INTEGER,
        vintage VARCHAR,
        name VARCHAR,
        open_date DATE,
        sampled_date DATE,
        added_to_cellartracker VARCHAR,
        notes VARCHAR,
        size INTEGER
    """

    target_columns = """
        id,
        vintage,
        name,
        open_date,
        sampled_date,
        added_to_cellartracker,
        notes,
        size
    """

    column_assignment = target_columns

    assert isinstance(db_filepath, str)

    db_methods.write_df_to_table(df, db_filepath, db_table_name, schema, target_columns, column_assignment)
    db_methods.display_table_info(db_filepath, db_table_name)


def main():
    init_raw_sample_tracker_table()


if __name__ == "__main__":
    main()
