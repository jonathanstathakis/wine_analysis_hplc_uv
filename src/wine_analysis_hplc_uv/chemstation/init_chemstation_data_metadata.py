"""
TODO:
-[ ] delete this file once confirmed that these are not needed.
"""

import collections
import os
from typing import List, Tuple


@ft.timeit
def uv_data_table_builder(uv_data_list, con):
    spectrum_table_name_prefix = "hplc_spectrum_"

    print("creating spectrum tables")
    for uv_data in uv_data_list:
        data = uv_data["data"]

        try:
            con.sql(
                f"CREATE TABLE {spectrum_table_name_prefix + str(uv_data['hash_key'])} AS SELECT * FROM data"
            )
        except Exception as e:
            print(e)

    num_unique_hash = len(set(d["hash_key"] for d in uv_data_list))
    print(num_unique_hash, "unique hash keys generated")

    # display result

    num_spectrum_tables = con.sql(
        f"""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_type='BASE TABLE' AND table_name LIKE '%{spectrum_table_name_prefix}%'
    """
    ).fetchone()[0]
    print(
        f"{num_spectrum_tables} spectrum tables created with name pattern '[{spectrum_table_name_prefix}]"
    )


@ft.timeit
def main():
    root_dir_path = "/Users/jonathan/0_jono_data"
    db_filepath = os.environ.get("WINE_AUTH_DB_PATH")


if __name__ == "__main__":
    main()
