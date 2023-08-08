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
            self.detection = ["'cuprac'", "raw"]
            self.samplecode = ["116", "111", "148", "90"]
            self.wine = [
                "2018 crawford river cabernets",
                "2014 perrier-jouët champagne belle epoque",
                "2020 vulka etna bianco cantine nicosia etna bianco",
                "2022 vinden estate the vinden headcase pokolbin blanc",
                "2019 shaw and smith shiraz balhannah",
            ]
            self.color = ["red", "white"]
            self.varietal = [
                "carignan blend",
                "cabernet-shiraz blend",
                "chardonnay",
                "riesling",
                "sangiovese blend",
            ]
            self.mins = [(0, 30), (15, 45)]
            self.wavelength = [
                254,
                190,
            ]
            # could add more here, this is a difficult problem. MVP means I should leave it as is,
            # can build up to slicing later down the track.

    gda = GetDataArgs()

    return gda


def test_samplecode(corecon, gda):
    # test samplecode
    for samplecode in gda.samplecode:
        wine_data = get_data.get_wine_data(corecon, samplecode=samplecode)
        print(wine_data.head())

        assert not wine_data.empty, samplecode
        assert wine_data.isna().sum().sum() == 0, samplecode


def test_detection(corecon, gda):
    for detection in gda.detection:
        wine_data = get_data.get_wine_data(corecon, detection=detection)

        assert not wine_data.empty, detection
        assert wine_data.isna().sum().sum() == 0, detection
        assert (
            wine_data["detection"].drop_duplicates().at[0] == detection
            or wine_data["detection"].isin(["cuprac", "raw"]).all()
        ), wine_data["detection"]
