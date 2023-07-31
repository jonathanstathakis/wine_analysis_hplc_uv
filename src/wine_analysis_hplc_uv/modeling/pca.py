"""

"""

import duckdb as db
from wine_analysis_hplc_uv.db_methods import db_methods
from wine_analysis_hplc_uv import definitions
from mydevtools.function_timer import timeit
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import os


def get_sampleids(con):
    sql_file = os.path.join(os.path.dirname(__file__), "test.sql")

    with open(sql_file, "r") as f:
        query = f.read()

    sampleids = con.sql(query).pl()
    return sampleids

    # subset_wines = tuple([wine[0] for wine in sampleids])
    # return subset_wines


@timeit
def get_sc_df(con):
    sampleids_ = get_sampleids(con)
    pl_data = db_methods.get_sc_df(
        con=con,
        sampleids=sampleids_,
        wavelength=[450],
        mins=(0, 30),
        detection=["cuprac"],
    )

    pd_df = pl_data.to_pandas()
    out_df = (
        pd_df.drop(["id", "mins", "wavelength", "detection"], axis=1)
        .assign(i=lambda df: df.groupby("wine").cumcount())
        .pivot(columns="wine", values="value", index="i")
    )
    pivoted_dfig, pivoted_data_ax = plt.subplots(1)
    sns.lineplot(data=pl_data, x="mins", y="value", hue="wine", ax=pivoted_data_ax)
    pivoted_dfig.suptitle("unpivoted data")
    pivoted_dfig.show()
    sns.lineplot(data=out_df)
    pivoted_dfig.suptitle("pivoted data")
    pivoted_data_ax.legend(bbox_to_anchor=(0.5, -0.15), loc="upper center")
    # pivoted_dfig.show()
    return out_df


def make_biplot(features, ldngs, scalePC1, scalePC2):
    fig, ax = plt.subplots(figsize=(14, 9))

    for i, feature in enumerate(features):
        ax.arrow(0, 0, ldngs[0, i], ldngs[1, i])
        ax.text(ldngs[0, i] * 1.15, ldngs[1, i] * 1.15, feature, fontsize=18)

    ax.scatter(scalePC1, scalePC2)
    ax.set_xlabel("PC1", fontsize=20)
    ax.set_ylabel("PC2", fontsize=20)
    ax.set_title("Figure 1", fontsize=20)
    fig.show()


def build_model(df):
    pca = PCA(n_components=2)
    PC1 = pca.fit_transform(df.values)[:, 0]
    PC2 = pca.fit_transform(df.values)[:, 1]
    ldngs = pca.components_
    scalePC1 = PC1 / (PC1.max() - PC1.min())
    scalePC2 = PC2 / (PC2.max() - PC2.min())
    features = df.columns.tolist()

    make_biplot(features=features, ldngs=ldngs, scalePC1=scalePC1, scalePC2=scalePC2)


def main():
    con = db.connect(definitions.DB_PATH)
    df = get_sc_df(con)
    build_model(df)


if __name__ == "__main__":
    main()
