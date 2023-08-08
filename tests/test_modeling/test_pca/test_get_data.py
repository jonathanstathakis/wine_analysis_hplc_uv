from numpy import core
from wine_analysis_hplc_uv.db_methods import get_data
import pytest
import pandas as pd
import duckdb as db


@pytest.fixture
def gda():
    class GetDataArgs:
        """
        the arguments for get_wine_data. iterate through each to test different options
        """

        def __init__(self):
            self.detection = ["cuprac", "raw"]
            self.samplecode = ["116", "111", "148", "90"]
            self.wine = [
                "2018 crawford river cabernets",
                "2022 vinden estate the vinden headcase pokolbin blanc",
                "2019 shaw and smith shiraz balhannah",
            ]
            self.color = ["red", "white", "orange"]
            self.varietal = [
                # "carignan blend",
                "cabernet-shiraz blend",
                "chardonnay",
                "riesling",
                "sangiovese blend",
            ]
            self.mins = [(0, 30), (15, 45)]
            self.wavelength = [
                254,
                190,
                # (254, 190)
            ]
            # could add more here, this is a difficult problem. MVP means I should leave it as is,
            # can build up to slicing later down the track.

    gda = GetDataArgs()

    return gda


def cat_var_assertions(corecon, keyword):
    wine_data_shape = corecon.sql(
        "select table_name, estimated_size, column_count from duckdb_tables where table_name='wine_data'"
    ).pl()
    print(wine_data_shape)
    assert wine_data_shape["estimated_size"][0] > 1
    assert wine_data_shape["column_count"][0] > 1

    # check that only 1 keyword value present
    tbl_detection_val = corecon.execute(
        f"SELECT DISTINCT $keyword from wine_data", {"keyword": keyword}
    ).fetchall()
    assert len(tbl_detection_val) == 1
    assert tbl_detection_val[0][0] == keyword


def test_samplecode(corecon, gda):
    # test samplecode
    for samplecode in gda.samplecode:
        print(samplecode)
        get_data.get_wine_data(corecon, samplecode=samplecode)
        cat_var_assertions(corecon, samplecode)


def test_detection(corecon, gda):
    for detection in gda.detection:
        get_data.get_wine_data(corecon, detection=detection)

        # check that rows and columns are greater than 1
        cat_var_assertions(corecon, detection)


def test_color(corecon, gda):
    for color in gda.color:
        print(color)
        get_data.get_wine_data(corecon, color=color)

        cat_var_assertions(corecon, color)


def test_wavelength(corecon, gda):
    for wavelength in gda.wavelength:
        print("\n", wavelength)
        get_data.get_wine_data(corecon, wavelength=wavelength)

        cat_var_assertions(corecon, wavelength)


def test_varietal(corecon, gda):
    for varietal in gda.varietal:
        print("\n", varietal)
        get_data.get_wine_data(corecon, varietal=varietal)

        cat_var_assertions(corecon, keyword=varietal)


def test_wine(corecon, gda):
    for wine in gda.wine:
        print("\n", wine)
        get_data.get_wine_data(corecon, wine=wine)
        cat_var_assertions(corecon, keyword=wine)


def test_mins(corecon, gda):
    for mins in gda.mins:
        print("\n", mins)
        get_data.get_wine_data(corecon, mins=mins)
        wd_mins = corecon.sql(
            "SELECT min(mins), max(mins), count(mins) from wine_data"
        ).df()
        print(mins)

        # test if minimum value is within 10% of stated mins. this happens because
        # measurement intervals can be diff for diff runs
        assert (mins[0] - wd_mins.at[0, "min(mins)"]) / mins[0] <= 0.1

        # test if maximum value is within 10% of stated max mins. as above
        assert (mins[1] - wd_mins.at[0, "max(mins)"]) / mins[1] <= 0.1
