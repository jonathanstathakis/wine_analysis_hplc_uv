from wine_analysis_hplc_uv.db_methods import get_data, pivot_wine_data
import pytest
import pandas as pd
import logging

logger = logging.getLogger(__name__)
pd.options.display.width = None
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
            # could add more here, this is a difficult problem. MVP means I should
            # leave it as is, can build up to slicing later down the track.

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
        "SELECT DISTINCT $keyword from wine_data", {"keyword": keyword}
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
    """
    lastmod: 2023-08-17 09:34:16

    Test that the pivot (pwd) of wine_data (wd) is sucessful.

    The expected output is a wide dataframe ~ 6000 rows long.

    The current tests are:

    1. check that the pwd shape is less than 10_000
    2. check that wd has more rows than pwd
    3. check that pwd has more columns than wd

    TODO:
    - [ ] expand on tests by including data type / content testing.
    - [ ] multiindex test
    - [ ] shape before and after pivot
    - [ ] get counts of unique values `n_unique` in pivot columns (i.e primary key i.e. 'id'), column count `n_col` and row count `n_row`. To calculate the expected shape, divide row count by `n_unique` to get pivot table `n_row`, add `n_unique` to `n_col` to get pivot table `n_col`. UPDATE: doesnt work, not sure why but the estimates are wrong.
    - [ ] cell contents
        - [ ] presence of nulls as `sum_null`. `sum_null` > 1 is an issue.

    """

    get_data.get_wine_data(
        corecon,
        wavelength=("254",),
        samplecode=(
            "100",
            "116",
        ),
    )

    # get number of unique wines in wd to predict the shape post-pivot.
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

    pwine = pivot_wine_data.pivot_wine_data(corecon)

    logger.info(f"\n{pwine}")
    logger.info(f"{type(pwine)}")

    # cols: 1. samplecode, 2. vars

    pw_shape = corecon.sql(
        """--sql
                      SELECT
        table_name, estimated_size, column_count
        FROM
        duckdb_tables()
        WHERE
        table_name='pwine_data'
                       """
    ).df()

    logger.info(f"shape:\n{pw_shape}")

    # simple shape test. Make sure that the pivot table has less than 10_000 rows

    assert pw_shape.at[0, "estimated_size"] < 10_000

    # now compare shape of wd and pwd. pwd should have more columns, wd should have more rows

    # rows
    assert wd_shape.at[0, "estimated_size"] > pw_shape.at[0, "estimated_size"]

    # columns
    assert wd_shape.at[0, "column_count"] < pw_shape.at[0, "column_count"]
