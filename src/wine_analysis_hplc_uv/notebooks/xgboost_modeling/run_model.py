import pandas as pd
import numpy as np
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import models

import logging

logging_level = logging.INFO
logger = logging.getLogger()
logger.setLevel(logging_level)

formatter = logging.Formatter(
    "%(asctime)s %(name)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(stream_handler)


def run_models():
    m = models.MyModel()
    m.run_model()


def main():
    run_models()


if __name__ == "__main__":
    main()
