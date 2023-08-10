from wine_analysis_hplc_uv import definitions
import duckdb as db
import pandas as pd
from wine_analysis_hplc_uv.db_methods import get_data
from wine_analysis_hplc_uv.modeling import pca
import matplotlib.pyplot as plt


def get_sample(con):
    get_data.get_wine_data(
        con,
        wavelength=(450,),
        detection=("cuprac",),
        color=("red",),
    )
    wines = con.sql(
        "SELECT distinct(samplecode), wine from wine_data using sample 5"
    ).fetchall()
    """
    [('124', '2022 mr. barval nebbia'), ('130', '2021 le juice fleurie fleurie gamay'), ('125', '2020 rockford moppa springs'), ('133', '2018 chalmers schioppettino dott.'), ('174', '2021 babo chianti')]
    ('124', '130', '125', '133', '174')
    """
    print(wines)
    wines = tuple([wine[0] for wine in wines])
    print(wines)

    get_data.get_wine_data(con, samplecode=wines, wavelength=(450,))

    wine_data = con.sql("SELECT * FROM wine_data").df()

    print(wine_data)
    pwine_data = pca.pivot_wine_data(wine_data)
    pwine_data.plot()
    plt.show()


def pivot_wine_data(con):
    """
    2023-08-10 07:22:03

    """
    con.sql(
        """--sql
            describe wine_data
            """
    ).show()

    con.sql(
        """--sql
            CREATE OR REPLACE TEMPORARY TABLE wine_data AS
            SELECT
            *
            from
            wine_data
            """
    )

    # add row numbers
    con.sql(
        """--sql
            CREATE TEMPORARY TABLE pwine_data AS
            SELECT
            wine,
            mins,
            value,
            ROW_NUMBER() OVER (PARTITION BY samplecode ORDER BY mins) AS obs_num
            FROM wine_data;
            """
    )

    con.sql(
        """--sql
            CREATE OR REPLACE TEMPORARY TABLE pwine_data AS
            SELECT *
            FROM (PIVOT (SELECT obs_num, wine, value FROM pwine_data) ON wine USING FIRST(value))
            ORDER BY obs_num
            """
    )

    con.sql(
        """--sql
            SELECT table_name, estimated_size, column_count from duckdb_tables where table_name='pwine_data'
            """
    ).show()

    con.sql(
        """--sql
            SELECT  table_name, column_name from duckdb_columns where table_name='pwine_data'
            """
    ).show()

    wines = con.sql(
        """--sql
            SELECT * EXCLUDE(obs_num) FROM pwine_data
            """
    ).df()

    wines.plot()
    plt.show()


from mydevtools.function_timer import timeit


@timeit
def main():
    con = db.connect(definitions.DB_PATH)
    # get_sample(con)
    get_data.get_wine_data(
        con,
        # samplecode=('124', '130', '125', '133', '174'),
        wavelength=(254,),
        # color=("red",),
        detection=("raw",),
    )
    pivot_wine_data(con)


if __name__ == "__main__":
    main()
