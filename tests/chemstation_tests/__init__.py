import logging

logging.basicConfig(level=logging.INFO)
chemstation_logger = logging.getLogger("wine_analysis_hplc_uv.chemstation")
chemstation_logger.setLevel(logging.INFO)
test_logger = logging.getLogger(__name__)