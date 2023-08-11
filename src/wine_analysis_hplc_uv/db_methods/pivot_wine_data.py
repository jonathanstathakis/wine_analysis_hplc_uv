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
            samplecode,
            mins,
            value,
            ROW_NUMBER() OVER (PARTITION BY samplecode ORDER BY mins) AS rowcount
            FROM wine_data;
            """
    )

    con.sql(
        """--sql
            CREATE OR REPLACE TEMPORARY TABLE pwine_data AS
            SELECT *
            FROM (PIVOT (SELECT rowcount, wine, value, samplecode, mins FROM pwine_data) ON samplecode USING FIRST(wine) as wine, FIRST(value) as value, FIRST(mins) as mins)
            ORDER BY rowcount
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
            SELECT * EXCLUDE(rowcount) FROM pwine_data
            """
    ).df()

    print(wines.head())
    wines = (
        wines.pipe(
            lambda df: df.set_axis(
                pd.MultiIndex.from_tuples(
                    [tuple(c.split("_")) for c in df.columns],
                    names=["samplecode", "vars"],
                ),
                axis=1,
            )
        )
        .rename_axis("i")
        # .reset_index(names=['i'])
        .stack(["samplecode"])
        .reset_index()
        .set_index(["i", "samplecode", "wine"])
        .unstack(["samplecode", "wine"])
        .reorder_levels(["samplecode", "wine", "vars"], axis=1)
        # .reset_index()
        # .pivot(columns=['samplecode','wine'], values=['mins','value'], index='i', value)
    )
    print(wines.head())
    print(wines.axes)
    print(wines.shape)

    # plt.show()


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