import logging

test_logger = logging.getLogger(__name__)

chemstation_logger = logging.getLogger("wine_analysis_hplc_uv.chemstation")
chemstation_logger.setLevel(logging.DEBUG)
