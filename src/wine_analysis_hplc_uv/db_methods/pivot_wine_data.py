from wine_analysis_hplc_uv import definitions
import duckdb as db
import pandas as pd
from wine_analysis_hplc_uv.db_methods import get_data
from wine_analysis_hplc_uv.modeling import pca
import matplotlib.pyplot as plt
import seaborn as sns


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

    """
    for a previously created long table 'wine_data' apply a pivot to reshape it into
    wide form to reduce memory size prior to transferring to python.
    
    
    1. Adds a numerical row index to each sample 'grouping' to enable pivoting
    2. pivot on samplecode as the unique identifier. The pivot merely reshapes rather
        than aggregating
        
    """
    con.sql(
        """--sql
            CREATE OR REPLACE TEMPORARY TABLE pwine_data AS
            SELECT *
            FROM (
                    PIVOT (
                        SELECT rowcount,
                            wine,
                            value,
                            samplecode,
                            mins
                        FROM (
                                SELECT wine,
                                    samplecode,
                                    mins,
                                    value,
                                    ROW_NUMBER() OVER (
                                        PARTITION BY samplecode
                                        ORDER BY mins
                                    ) AS rowcount
                                FROM wine_data
                            )
                    ) ON samplecode
                    USING
                        FIRST(wine) as wine,
                        FIRST(value) as value,
                        FIRST(mins) as mins
                )
            """
    )

    wine = con.sql(
        """--sql
            SELECT * EXCLUDE(rowcount) FROM pwine_data
            --USING
            --SAMPLE
            --5
            """
    ).df()

    wine = wine.pipe(
        lambda df: df.set_axis(
            pd.MultiIndex.from_tuples(
                [tuple(c.split("_")) for c in df.columns],
                names=["samplecode", "vars"],
            ),
            axis=1,
        )
    )

    return wine


def stack_df(df):
    """
    reshape an unstacked multi-index column df to a stacked df for plotting purposes.

    probs not gna use this but its a useful example for personal use.
    """

    df = (
        df.pipe(
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
        .sort_index(axis=1, level=0, sort_remaining=True)
    )

    return df
