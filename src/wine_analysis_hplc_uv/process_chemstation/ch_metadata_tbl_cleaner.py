"""
Contain all the methods to clean the chemstation metadata table before input into super_table_pipe.

Acts on a local table which is written by prototype_code/chemstation_db_tables_metadata_data.py
"""
import duckdb as db
import numpy as np
import pandas as pd

from ..db_methods import db_methods
from ..df_methods import df_cleaning_methods


def ch_metadata_tbl_cleaner(
    db_filepath: str, raw_table_name: str, clean_tbl_name: str
) -> None:
    """
    A pipe function that gets the raw chemstation table, cleans it and writes back to the db
    """
    df = pd.DataFrame()
    print(f"connecting to {db_filepath}..\n")
    with db.connect(db_filepath) as con:
        df = con.sql(
            f"""
            SELECT
                notebook, date, method, path, sequence_name, hash_key
            FROM
                {raw_table_name}
            """
        ).df()

    df = (
        df.pipe(df_cleaning_methods.df_string_cleaner)
        .pipe(rename_chemstation_metadata_cols)
        .pipe(format_acq_date)
        .pipe(chemstation_id_cleaner)
        .pipe(chemstation_metadata_drop_unwanted_runs)
    )

    write_cleaned_ch_metadata_tbl_to_db(df, db_filepath, clean_tbl_name)

    return None


def format_acq_date(df):
    df["acq_date"] = pd.to_datetime(df["acq_date"]).dt.strftime("%Y-%m-%d")
    return df


def rename_chemstation_metadata_cols(df):
    df = df.rename(
        {"notebook": "id", "date": "acq_date", "method": "acq_method"}, axis=1
    )
    return df


def chemstation_metadata_drop_unwanted_runs(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        ~(df["join_samplecode"] == "coffee")
        & ~(df["join_samplecode"] == "lor-ristretto")
        & ~(df["join_samplecode"] == "espresso")
        & ~(df["join_samplecode"] == "lor-ristretto_column-check")
        & ~(df["join_samplecode"] == "nc1")
        & ~(df["exp_id"].isna())
    ]
    df = library_id_replacer(df)

    print(
        "\nthe following join_samplecode's are not digits and will cause an error when writing the table:\n"
    )
    print(df[~(df["join_samplecode"].str.isdigit())])

    return df


def write_df_to_table_variables():
    schema = """
    exp_id VARCHAR,
    acq_date DATE,
    acq_method VARCHAR,
    path VARCHAR,
    sequence_name VARCHAR,
    hash_key VARCHAR,
    join_samplecode VARCHAR
    """

    column_names = """
    exp_id,
    acq_date,
    acq_method,
    path,
    sequence_name,
    hash_key,
    join_samplecode
    """

    return schema, column_names, column_names


def four_digit_id_to_two_digit(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename({"id": "exp_id"}, axis=1)
    df["join_samplecode"] = (
        df["exp_id"].astype(str).apply(lambda x: x[1:3] if len(x) == 4 else x)
    )
    return df


def string_id_to_digit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces the id of a number of runs with their 2 digit id's as stated in the sample tracker.
    """
    # 1. z3 to 00
    df["join_samplecode"] = df["join_samplecode"].replace({"z3": "00"})
    return df


def chemstation_id_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    print("cleaning chemstation run id's")
    df = four_digit_id_to_two_digit(df)
    df = string_id_to_digit(df)
    return df


def rename_wine_deg_wines(join_samplecode_series: pd.Series):
    """
    Use regex to find the wines exp_id then replace with the sample_tracker id.add()
    pattern = .[01]..
    """
    # Define the regex pattern and replacement mapping
    pattern = r"^[nea](01|02|03)"
    replacement = {"01": "103", "02": "104", "03": "105"}

    # Replace the strings in the 'join_samplecode' column using the regex pattern and replacement mapping
    join_samplecode_series = join_samplecode_series.replace(
        pattern, lambda x: replacement[x.group(1)], regex=True
    )

    return join_samplecode_series


def library_id_replacer(df: pd.DataFrame) -> pd.DataFrame:
    replace_dict = {
        "2021-debortoli-cabernet-merlot_avantor|debertoli_cs": "72",
        "stoney-rise-pn_02-21": "73",
        "crawford-cab_02-21": "74",
        "hey-malbec_02-21": "75",
        "koerner-nellucio-02-21": "76",
    }

    df["join_samplecode"] = df["join_samplecode"].replace(replace_dict, regex=True)

    try:
        df["join_samplecode"] = df["join_samplecode"].apply(rename_wine_deg_wines)
    except:
        print(df.columns)
    return df


def write_cleaned_ch_metadata_tbl_to_db(
    df: pd.DataFrame, db_filepath: str, raw_table_name: str
) -> None:
    """
    1. create a table name based on the raw name, replacing 'raw' for 'cleaned'.
    2. get the information required to write the cleaned df to the db.
    3. write the df to db
    """
    new_table_name = raw_table_name.replace("raw", "cleaned")
    schema, table_column_names, df_column_names = write_df_to_table_variables()

    try:
        print(f"\nwriting df of shape {df.shape}, columns: {df.columns} to db\n")
        db_methods.write_df_to_table(
            df, db_filepath, new_table_name, schema, table_column_names, df_column_names
        )
    except Exception as e:
        print(
            f"Exception encountered when writing cleaned_chemstation_metadata_table to database: {e}"
        )
    return None


def main():
    con = db.connect("wine_auth_db.db")
    raw_table_name = "raw_chemstation_metadata"
    ch_metadata_tbl_cleaner(con, raw_table_name)


if __name__ == "__main__":
    main()
