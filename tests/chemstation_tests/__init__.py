from . import logging, test_logger

chemstation_logger = logging.getLogger("wine_analysis_hplc_uv.chemstation")
chemstation_logger.setLevel(logging.DEBUG)
