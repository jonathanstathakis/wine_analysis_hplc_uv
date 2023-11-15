import logging

logger = logging.getLogger(__name__)

from sklearn import datasets

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract
from dataclasses import dataclass
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import kwarg_classes

import pandas as pd


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


class RawRedVarietalData(dataextract.DataExtractor, data_pipeline.DataPipeline):
    def __init__(
        self, db_path: str, ext_kwargs: dict = dict(), dp_kwargs: dict = dict()
    ) -> tuple:
        dataextract.DataExtractor.__init__(self, db_path=db_path, **ext_kwargs)
        data_pipeline.DataPipeline.__init__(self, self.raw_data, **dp_kwargs)


class CUPRACRedVarietalData(dataextract.DataExtractor, data_pipeline.DataPipeline):
    def __init__(self, db_path: str) -> tuple:
        dataextract.DataExtractor.__init__(self, db_path=db_path)
        data_pipeline.DataPipeline.__init__(
            self, self.raw_data, kwargs.data_pipeline_kwargs
        )
