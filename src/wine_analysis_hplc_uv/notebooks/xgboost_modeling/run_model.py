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
    runs = dict()

    for i in range(1, 6):
        m = models.MyModel()

        confm, classreport = m.run_model(model_type="gridCV")

        runs[i] = dict()
        classreport.insert(0, "runnum", i)
        runs[i]["classreport"] = classreport

        # print(i)
        # print(confm)
        # print(classreport)

    reports = pd.concat([runs[run]["classreport"] for run in runs])

    print(reports)

    print(f"mean accuracy: {reports.groupby('runnum')['accuracy'].first().mean()}")


def main():
    run_models()


if __name__ == "__main__":
    main()
