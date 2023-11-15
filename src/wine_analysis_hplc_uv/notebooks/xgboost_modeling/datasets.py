import logging

logger = logging.getLogger(__name__)

from sklearn import datasets

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract

import pandas as pd


class ExtractTransformData(dataextract.DataExtractor, data_pipeline.DataPipeline):
    def __init__(self, db_path):
        dataextract.DataExtractor.__init__(self, db_path=db_path)
        self.detection: tuple = (None,)
        self.samplecode: tuple = (None,)
        self.exclude_samplecodes: tuple = (None,)
        self.exclude_ids: tuple = (None,)
        self.color: tuple = (None,)
        self.wavelengths: int | list | tuple = 256
        self.varietal: tuple = (None,)
        self.wine: tuple = (None,)
        self.mins: tuple = (None, None)

    def extract_signal_process_pipeline(
        self, process_frame_kwargs: dict = dict()
    ) -> pd.DataFrame:
        """
        extract_signal_process_pipeline A pipeline running from the database to a standardized matrix of signals

        Intended to be used to extract, clean and transform data prior to submission to Sklearn pipeline.

        It includes:
        1. retrieval of the raw data with hardcoded selection values
        2. signal processing to standardize the sample signals and remove noise

        :param process_frame_kwargs: kwargs for `DataPipeline.process_frame`, defaults to dict()
        :type process_frame_kwargs: dict, optional
        :return: returns a dataframe `self.pro_data_`
        :rtype: pd.DataFrame
        """

        self.create_subset_table(
            detection=self.detection_,
            exclude_ids=self.exclude_ids,
            wavelengths=self.wavelengths,
            color=self.color,
        )

        self.raw_data_ = self.get_tbl_as_df()

        self.pro_data_ = self.raw_data_.pipe(
            self.signal_preprocess, **process_frame_kwargs
        )

        return self.pro_data_


class TestData:
    def __init__(self):
        self.getdata()
        self.prep_for_model()

    def getdata(self):
        # get the iris dataset and prep it to resemble my dataset
        irisbunch = datasets.load_iris()
        self.data = pd.DataFrame(data=irisbunch.data, columns=irisbunch.feature_names)
        self.data["target"] = irisbunch.target
        self.data.target = self.data.target.replace(
            {
                0: irisbunch.target_names[0],
                1: irisbunch.target_names[1],
                2: irisbunch.target_names[2],
            }
        )

    def prep_for_model(self):
        self.x = self.data.drop("target", axis=1)
        self.y = self.data.target


class RawRedVarietalData(ExtractTransformData):
    def __init__(self, db_path: str) -> tuple:
        ExtractTransformData.__init__(self, db_path=db_path)

        self.detection_ = ("raw",)
        self.exclude_ids_ = tuple(definitions.EXCLUDEIDS.values())
        self.wavelengths_ = (256,)
        self.color_ = ("red",)


class CUPRACRedVarietalData(ExtractTransformData):
    def __init__(self, db_path: str) -> tuple:
        super().__init__(db_path=db_path)
        self.detection_ = ("cuprac",)
        self.exclude_ids_ = tuple(definitions.EXCLUDEIDS.values())
        self.wavelengths_ = (450,)
        self.varietal = ("shiraz", "pinot noir", "chardonnay")
