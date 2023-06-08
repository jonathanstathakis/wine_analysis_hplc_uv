import duckdb as db
import pandas as pd

from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv.google_sheets_api import google_sheets_api
from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods

from wine_analysis_hplc_uv.sampletracker import logger


def init_raw_sample_tracker_table(db_filepath: str, table_name: str) -> None:
    # download the current sample tracker table
    df = sample_tracker_methods.sample_tracker_df_builder()
    df = df.replace({"": None})
    sampletracker_to_db(df, db_filepath, table_name)
    db_methods.display_table_info(db_filepath, table_name)
    return None


def sampletracker_to_db(df: pd.DataFrame, db_filepath: str, db_table_name: str):
    logger.debug(f"{__name__}")
    logger.debug(f"creating table {db_table_name} in {db_filepath}")

    target_columns = """
        sampler,
        detection,
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

    db_methods.write_df_to_table(
        df, db_filepath, db_table_name, schema, target_columns, column_assignment
    )
    db_methods.display_table_info(db_filepath, db_table_name)


def main():
    init_raw_sample_tracker_table()


if __name__ == "__main__":
    main()
