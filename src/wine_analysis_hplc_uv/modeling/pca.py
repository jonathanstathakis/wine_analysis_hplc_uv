import pandas as pd
import polars as pl
import duckdb as db
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv import definitions
from mydevtools.function_timer import timeit
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import os
import logging

logger = logging.getLogger(__name__)


@timeit
def pivot_wine_pddf(df):
    """
    Pivot wine_data on wines to produce a wide df with columns labeled with wine names
    and consisting of absorbance values.

    """
    logger.info(f"before pivot, shape: {df.shape}")
    out_df = (
        df.loc[:, ["id", "samplecode", "wine", "value"]]
        .assign(i=lambda df: df.groupby(["id"]).cumcount())
        .assign(code_wine=lambda df: df["samplecode"] + "_-" + df["wine"])
        .pivot(columns="code_wine", values="value", index="i")
    )
    logger.info(f"after pivot, shape: {out_df.shape}..")
    logger.info(f"{out_df.isna().sum()}")
    logger.info(f"\n{out_df}")

    return out_df


def plot_wine_data(df, ax):
    z = sns.lineplot(data=df, ax=ax, legend=False)
    a = ax.set_title("pivoted data")
    b = ax.set_xlabel("observation")
    c = ax.set_ylabel("abs. (mAU)")
    # ax.legend(bbox_to_anchor=(0.5, -0.15), loc="upper center")
    return ax


def build_model(df, ax):
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    x = df.fillna(0).values
    x = scaler.fit_transform(x)

    pca = PCA(n_components=2)
    model = pca.fit_transform(X=x)
    PC1 = model[:, 0]
    PC2 = model[:, 1]

    ldngs = pca.components_
    scalePC1 = PC1 / (PC1.max() - PC1.min())
    scalePC2 = PC2 / (PC2.max() - PC2.min())
    features = df.columns.tolist()

    for i, feature in enumerate(features):
        a = ax.arrow(0, 0, ldngs[0, i], ldngs[1, i])
        b = ax.text(ldngs[0, i] * 1.15, ldngs[1, i] * 1.15, feature, fontsize=8)

    c = ax.scatter(scalePC1, scalePC2)
    d = ax.set_xlabel("PC1")
    e = ax.set_ylabel("PC2")
    f = ax.set_title("PCA Biplot")

    return ax


def build_figure(data):
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

    a = plot_wine_data(data, ax=ax1)
    b = build_model(data, ax=ax2)

    return fig


def get_data(con):
    wine_data = get_data.get_wine_data(con)
    pwine_data = pivot_wine_pddf(wine_data)
    return pwine_data


def main():
    con = db.connect(definitions.DB_PATH)
    pwine_data = get_data(con)
    plt1, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
    plot_wine_data(pwine_data, ax=ax1)
    build_model(pwine_data, ax=ax2)
    fig = build_figure(pwine_data)
    fig.tight_layout()


if __name__ == "__main__":
    main()
