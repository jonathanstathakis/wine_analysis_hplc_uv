"""
1. get the data - processed. Needs to be the varietal data.
2. set up the PCA analysis
"""
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import kwarg_classes
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import datasets
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import models
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
import numpy as np
import seaborn.objects as so
import pandas as pd


class myPCA:
    def __init__(self, db_path: str, data_kwargs: dict = dict()) -> None:
        self.data = self.get_data(db_path).dropna()

        self.melt_df = self.data.melt(
            ignore_index=False, value_name="abs"
        ).reset_index()

        print(self.data.index)

        # pd.cut(self.melt_df.mins, self.melt_df.mins.max())

        # (
        #     self.melt_df
        #     .reset_index()
        #     .pipe(so.Plot, x="mins", y="abs", color="code_wine")
        #     .add(so.Line())
        #     .show()
        # )

        # so.Plot(data=self.data, x=)
        # print(self.data.T.reset_index().dropna(axis=1))

    def get_data(self, db_path: str, kwargs: dict = dict()):
        rrv = datasets.RawRedVarietalData(db_path=db_path)
        rrv.extract_signal_process_pipeline(kwargs)

        return rrv.pro_data_


def main():
    mypca = myPCA(definitions.DB_PATH)

    # ds = datasets.RawRedVarietalData(
    #     definitions.DB_PATH,
    #     ext_kwargs=kwarg_classes.DefaultETKwargs().extractor_kwargs,
    #     dp_kwargs=kwarg_classes.DefaultETKwargs().data_pipeline_kwargs,
    # )


if __name__ == "__main__":
    main()
