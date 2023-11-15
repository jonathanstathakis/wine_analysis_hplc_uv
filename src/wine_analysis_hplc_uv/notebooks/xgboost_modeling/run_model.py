"""
TODO:
- [ ] move the transform_dataset actions to the signal process pipeline.
"""

import pandas as pd
import numpy as np
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import models
from wine_analysis_hplc_uv.notebooks.xgboost_modeling.smotetracker import smotes

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


def run_model(model):
    score_df, best_est = model.run_model(model_type="gridCV")

    return score_df, best_est


def main():
    redrawmodel = models.RawRedVarietalModel()
    run_model(redrawmodel)

    cupracredmodel = models.CUPRACRedVarietalModel()()
    run_model(cupracredmodel)


if __name__ == "__main__":
    main()
