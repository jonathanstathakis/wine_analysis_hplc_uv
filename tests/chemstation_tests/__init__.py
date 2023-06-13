import logging

logging.basicConfig(level=logging.DEBUG)
chemstation_logger = logging.getLogger("wine_analysis_hplc_uv.chemstation")
chemstation_logger.setLevel(logging.DEBUG)
test_logger = logging.getLogger(__name__)
