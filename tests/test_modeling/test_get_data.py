from wine_analysis_hplc_uv.db_methods import get_data, pivot_wine_data
import pytest
import pandas as pd
import duckdb as db
import logging

logger = logging.getLogger(__name__)
pd.options.display.width = None
pd.options.display.show_dimensions = True
pd.options.display.max_colwidth = 20
pd.options.display.max_rows = 20
pd.options.display.max_columns = 15
pd.options.display.colheader_justify = "left"


@pytest.fixture
def gda():
    class GetDataArgs:
        """
        the arguments for get_wine_data. iterate through each to test different options
        """

        def __init__(self):
            self.detection = [("cuprac",), ("raw",)]
            self.samplecode = [
                ("116",),
                ("111",),
                ("148",),
                ("90",),
                ("116", "111"),
            ]
            self.wine = [
                ("2018 crawford river cabernets",),
                ("2022 vinden estate the vinden headcase pokolbin blanc",),
                ("2019 shaw and smith shiraz balhannah",),
                (
                    "2022 vinden estate the vinden headcase pokolbin blanc",
                    "2019 shaw and smith shiraz balhannah",
                ),
            ]
            self.color = [("red",), ("white",), ("orange",), ("white", "orange")]
            self.varietal = [
                # "carignan blend",
                ("cabernet-shiraz blend",),
                ("chardonnay",),
                ("riesling",),
                ("sangiovese blend",),
                ("shiraz", "riesling"),
            ]
            self.mins = [(0, 30), (15, 45)]
            self.wavelength = [
                (254,),
                (190,),
                (254, 190),
            ]
            # could add more here, this is a difficult problem. MVP means I should leave it as is,
            # can build up to slicing later down the track.

    gda = GetDataArgs()

    return gda


def cat_var_assertions(corecon, keyword):
    wine_data_shape = corecon.sql(
        "select table_name, estimated_size, column_count from duckdb_tables where"
        " table_name='wine_data'"
    ).pl()
    print(wine_data_shape)
    assert wine_data_shape["estimated_size"][0] > 1
    assert wine_data_shape["column_count"][0] > 1

    # check that only 1 keyword value present
    tbl_detection_val = corecon.execute(
        f"SELECT DISTINCT $keyword from wine_data", {"keyword": keyword}
    ).fetchall()
    assert len(tbl_detection_val) == 1
    assert tuple(tbl_detection_val[0][0]) == keyword


def test_sliceby_samplecode(corecon, gda):
    # test samplecode
    for samplecode in gda.samplecode:
        logger.info(f"slicing by: {samplecode}")
        get_data.get_wine_data(corecon, samplecode=samplecode)
        cat_var_assertions(corecon, samplecode)


def test_sliceby_detection(corecon, gda):
    for detection in gda.detection:
        logger.info(f"slicing by: {detection}")
        get_data.get_wine_data(corecon, detection=detection)

        # check that rows and columns are greater than 1
        cat_var_assertions(corecon, detection)


def test_sliceby_color(corecon, gda):
    for color in gda.color:
        logger.info(f"slicing by: {color}")
        get_data.get_wine_data(corecon, color=color)

        cat_var_assertions(corecon, color)


def test_sliceby_wavelength(corecon, gda):
    for wavelength in gda.wavelength:
        logger.info(f"slicing by: {wavelength}")
        get_data.get_wine_data(
            corecon,
            wavelength=wavelength,
            # detection=('cuprac',)
        )

        cat_var_assertions(corecon, wavelength)


def test_sliceby_varietal(corecon, gda):
    for varietal in gda.varietal:
        logger.info(f"slicing by: {varietal}")
        get_data.get_wine_data(corecon, varietal=varietal)

        cat_var_assertions(corecon, keyword=varietal)


def test_sliceby_wine(corecon, gda):
    for wine in gda.wine:
        logger.info(f"slicing by: {wine}")
        get_data.get_wine_data(corecon, wine=wine)
        cat_var_assertions(corecon, keyword=wine)
        print(
            corecon.sql(
                """--sql
                        SELECT
                        wavelength
                        from
                        wine_data
                        """
            ).fetchall()
        )


def test_sliceby_mins(corecon, gda):
    for mins in gda.mins:
        logger.info(f"slicing by: {mins}")
        get_data.get_wine_data(
            corecon,
            mins=mins,
            wavelength=(254,),
            wine=("2022 vinden estate the vinden headcase pokolbin blanc",),
        )
        wd_mins = corecon.sql(
            "SELECT min(mins), max(mins), count(mins) from wine_data"
        ).df()
        print(mins)

        # test if minimum value is within 10% of stated mins. this happens because
        # measurement intervals can be diff for diff runs
        assert (mins[0] - wd_mins.at[0, "min(mins)"]) / mins[0] <= 0.1

        # test if maximum value is within 10% of stated max mins. as above
        assert (mins[1] - wd_mins.at[0, "max(mins)"]) / mins[1] <= 0.1


def test_pivot_wine_data(corecon, gda):
    get_data.get_wine_data(corecon, wavelength=("254",))

    n_wines = len(
        corecon.execute(
            """--sql
                              SELECT
                              DISTINCT samplecode
                              FROM
                              wine_data
                              """
        ).fetchall()
    )

    wd_shape = corecon.execute(
        """--sql
        SELECT
        table_name, estimated_size, column_count
        FROM
        duckdb_tables()
        WHERE
        table_name='wine_data'
        """
    ).df()

    logger.info(n_wines)
    logger.info(f"\n{wd_shape}")
    # logger.info(n_cols)

    exp_pivot_n_rows = wd_shape["estimated_size"] / n_wines
    logger.info(exp_pivot_n_rows)
    # exp_pivot_n_cols = int(*n_wines)
    wine = pivot_wine_data.pivot_wine_data(corecon)

    # cols: 1. samplecode, 2. vars
    (
        wine
        # .dropna()
        .stack(0)
        .assign(av_mins=lambda df: df.groupby("i")["mins"].mean())
        .unstack("samplecode")
        # .pipe(lambda df: df if logger.info(f"\n{df.iloc[:5,:5]}") is None else df)
        .pipe(lambda df: df if logger.info(f"\n{df.shape}") is None else df)
        .pipe(lambda df: df if logger.info(f"\n{df.loc[:5,'av_mins']}") is None else df)
        .pipe(lambda df: df if logger.info(f"\n{df.columns}") is None else df)
    )

    # pw_shape = corecon.sql("""--sql
    #                   SELECT
    #     table_name, estimated_size, column_count
    #     FROM
    #     duckdb_tables()
    #     WHERE
    #     table_name='pwine_data'
    #                    """)

    # logger.info(f"\n{pw_shape}")
    # logger.info("after pivot, df:")
    # logger.info(wine.shape)
    # logger.info(f"\n{wine.columns[0:5]}")
    # logger.info(f"\n{wine}")

    # assert (
    #     wine
    #     .stack([0])
    #     .isna()
    #     #.groupby('samplecode')
    #     .sum().sum()
    # ) == 0
