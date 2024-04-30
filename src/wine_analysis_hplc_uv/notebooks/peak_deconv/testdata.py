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
    append = False
    extractor_kwargs = dict(
        _table_name="testdata",
        detection=("raw",),
        wavelengths=(256,),
        varietal=("shiraz",),
        mins=(0, 27),
    )
    data_pipeline_kwargs = dict(
        resample_kwgs=dict(
            grouper=["id", "code_wine"],
            time_col="mins",
            original_freqstr="0.4S",
            resample_freqstr="0.4S",
        ),
        melt_kwgs=dict(
            id_vars=["detection", "color", "varietal", "id", "code_wine", "mins"],
            value_name="signal",
            var_name="wavelength",
        ),
        smooth_kwgs=dict(
            smooth_kwgs=dict(
                grouper=["id", "wavelength"],
                col="signal",
            ),
            append=append,
        ),
        bline_sub_kwgs=dict(bypass=True),
        pivot_kwgs=dict(bypass=True),
    )


class TestData(
    TestDataKwargs,
):
    def __init__(self, con: db.DuckDBPyConnection):
        self._con = con
        self.extractor = dataextract.DataExtractor(self._con, **self.extractor_kwargs)
        self.extractor.load_data()
        self._raw_data = None
        self._pipeline = data_pipeline.DataPipeline(**self.data_pipeline_kwargs)

    def get_raw_samples(self, key: str = "code_wine", x: int = 5):
        """
        :param key: primary identifier of the sample
        :param x: the number of samples
        """
        self._raw_data = self.extractor.get_first_x_raw_samples(key=key, x=x).rename(
            {"mins": "time", "nm_256": "signal"}, axis=1
        )

        return self._raw_data

    def get_processed_samples(self, kwargs: dict = dict()):
        """
        get_processed_samples get first 'x' processed samples

        _extended_summary_

        :param key: _description_
        :type key: str
        :param x: _description_
        :type x: int
        """

        # get the first x samples from the raw table
        self._raw_data = self.extractor.get_first_x_raw_samples(**kwargs)

        # apply the preprocess pipe to the first x samples
        self._pro_data = self._pipeline.signal_preprocess(self._raw_data)

        # rename samples to match hply_py specs
        self._pro_data = self._pro_data.reset_index().rename({"mins": "time"}, axis=1)

        return self._pro_data


def main():
    from wine_analysis_hplc_uv import definitions

    con = db.connect(definitions.DB_PATH)
    td = TestData(con)

    samples = td.get_raw_samples(key="code_wine", x=1)
    breakpoint()


if __name__ == "__main__":
    main()
