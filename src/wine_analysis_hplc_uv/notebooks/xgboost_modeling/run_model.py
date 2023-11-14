import pandas as pd
import numpy as np
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import models


def run_models():
    m = models.MyModel()
    m.run_model()


def main():
    run_models()


if __name__ == "__main__":
    main()
