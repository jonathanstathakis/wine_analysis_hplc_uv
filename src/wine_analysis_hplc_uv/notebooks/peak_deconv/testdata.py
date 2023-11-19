"""
2023-11-20 09:28:27

Test dataset, Raw Shiraz at 256nm.
"""

from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract
import logging
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import kwarg_classes

logger = logging.getLogger(__name__)


class TestDataKwargs(kwarg_classes.DefaultETKwargs):
    extractor_kwargs = dict(
        detection=("raw",),
        wavelengths=(256,),
        varietal=("shiraz",),
        mins=(0, 27),
    )


class TestData(
    dataextract.DataExtractor,
    data_pipeline.DataPipeline,
    TestDataKwargs,
):
    def __init__(self, db_path):
        logger.info(f"using test dataset with: {self.extractor_kwargs}")
        dataextract.DataExtractor.__init__(
            self, db_path=db_path, **self.extractor_kwargs
        )
        data_pipeline.DataPipeline.__init__(
            self, self.raw_data, **self.data_pipeline_kwargs
        )
