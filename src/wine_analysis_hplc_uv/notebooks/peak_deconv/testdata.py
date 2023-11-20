"""
2023-11-20 09:28:27

Test dataset, Raw Shiraz at 256nm.
"""

from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract
import logging
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import kwarg_classes
import duckdb as db
import pandas as pd

logger = logging.getLogger(__name__)


class TestDataKwargs(kwarg_classes.DefaultETKwargs):
    extractor_kwargs = dict(
        table_name="testdata",
        detection=("raw",),
        wavelengths=(256,),
        varietal=("shiraz",),
        mins=(0, 27),
    )


class TestData(
    TestDataKwargs,
):
    def __init__(self, db_path):
        self.db_path = db_path
        self.extractor = dataextract.DataExtractor(
            self.db_path, **self.extractor_kwargs
        )
        self.raw_data = None
        self.pipeline = data_pipeline.DataPipeline(
            self.raw_data, **self.data_pipeline_kwargs
        )

    def get_samples(self, key: str, x: int):
        samples = self.extractor.get_first_x_samples(key=key, x=x)

        return samples


def main():
    from wine_analysis_hplc_uv import definitions

    td = TestData(db_path=definitions.DB_PATH)

    samples = td.get_samples(key="code_wine", x=2)


if __name__ == "__main__":
    main()
