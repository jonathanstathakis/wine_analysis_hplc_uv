"""
1. get the data - processed. Needs to be the varietal data.
2. set up the PCA analysis
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn import decomposition, pipeline, preprocessing
from deprecated import deprecated
from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.modeling.xgboost import data_prep, datasets

deprecated(reason="appraoch is obsolete")


class myPCA:
    def __init__(self, db_path: str, data_kwargs: dict = dict()) -> None:
        self.pipeline = pipeline.Pipeline(
            [
                ("scaler", preprocessing.StandardScaler()),
                ("pca", decomposition.PCA(n_components=3)),
            ]
        )

        self.data = self.get_data(db_path)

        # # plot all the data as an overlay
        # (
        #     self.data
        #     .melt(
        #     ignore_index=False, value_name="abs"
        #     )
        #     .reset_index()
        #     .pipe(so.Plot, x="mins", y="abs", color="code_wine")
        #     .add(so.Line(), legend=False)
        #     .show(block=True)
        # )

        dp = data_prep.DataPrepper()

        data = (
            self.data.T.reset_index()
            .pipe(dp.select_included_classes, target_col="varietal", min_num_samples=6)
            .reset_index(drop=True)
        )

        X = data.drop(["varietal", "color", "detection", "id", "code_wine"], axis=1)
        y = data["varietal"]

        # 2024-05-14 13:14:53. Line below may be needed, linting may have accidentally removed its call?
        # le = LabelEncoder()

        Xt = self.pipeline.fit_transform(X)
        Xt = pd.DataFrame(Xt, index=y).reset_index()

        Xt = Xt.assign(code_wine=data.code_wine)

        self.plotly_3dscatter(Xt)

    def plotly_3dscatter(self, Xt):
        fig = px.scatter_3d(Xt, x=0, y=1, z=2, color="varietal", hover_data="code_wine")
        fig.show()

    def get_data(self, db_path: str, kwargs: dict = dict()):
        rrv = datasets.PCARawRedVarietalData(db_path=db_path)
        rrv._pro_data

        return rrv._pro_data

    def matplotlib_3dscatter(X):
        fig = plt.figure(1, figsize=(4, 3))
        plt.clf()

        ax = fig.add_subplot(111, projection="3d", elev=48, azim=134)
        ax.set_position([0, 0, 0.95, 1])

        plt.cla()

        for varietal in X.varietal.unique():
            print(varietal)
            ax.text3D(
                X.loc[lambda df: df.varietal == varietal, 0].mean(),
                X.loc[lambda df: df.varietal == varietal, 1].mean() + 1.5,
                X.loc[lambda df: df.varietal == varietal, 2].mean(),
                varietal,
                horizontalalignment="center",
                bbox=dict(alpha=0.5, edgecolor="w", facecolor="w"),
            )

        y = np.choose(X.varietal.unique(), [1, 2, 0]).astype(float)

        ax.scatter(
            X.loc[:, 0],
            X.loc[:, 1],
            X.loc[:, 2],
            #    c=y,
            #    cmap=plt.cm.nipy_spectral,
            #    edgecolor='k',
            #    s=100
        )
        plt.show()

        for name, label in [("Setosa", 0), ("Versicolour", 1), ("Virginica", 2)]:
            # add the text box at the intersect of the mean of the three components of each class
            ax.text3D(
                X[y == label, 0].mean(),
                X[y == label, 1].mean() + 1.5,
                X[y == label, 2].mean(),
                name,
                horizontalalignment="center",
                bbox=dict(alpha=0.5, edgecolor="w", facecolor="w"),
            )
        # Reorder the labels to have colors matching the cluster results
        y = np.choose(y, [1, 2, 0]).astype(float)

        # plot each sample at a coordinate depicted by its first three PC.
        ax.scatter(
            X[:, 0],
            X[:, 1],
            X[:, 2],
            c=y,
            cmap=plt.cm.nipy_spectral,
            edgecolor="k",
            s=100,
        )

        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])
        ax.zaxis.set_ticklabels([])

        plt.show()


def main():
    myPCA(definitions.DB_PATH)

    # ds = datasets.RawRedVarietalData(
    #     definitions.DB_PATH,
    #     ext_kwargs=kwarg_classes.DefaultETKwargs().extractor_kwargs,
    #     dp_kwargs=kwarg_classes.DefaultETKwargs().data_pipeline_kwargs,
    # )


if __name__ == "__main__":
    main()
