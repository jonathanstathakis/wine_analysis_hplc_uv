import pytest
import logging
import duckdb as db
from wine_analysis_hplc_uv import db_methods, definitions
from wine_analysis_hplc_uv.modeling import pca


def test_get_sample_ids(corecon):
    sampleids = pca.get_sampleids(corecon)
    # assert sampleids
    # assert len(sampleids) == 10
    logger.info(f"\n{sampleids}")
