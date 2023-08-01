"""

"""
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


def get_wine_data(con):
    """
    Select all CUPRAC wines, getting their metadata as well by first joining the
    sample tracker and cellar tracker tables, then chemstation metadata then finally
    chemstation data table.

    ## Tables in DB

    0        c_cellar_tracker
    1  c_chemstation_metadata
    2        c_sample_tracker
    3          cellar_tracker
    4    chemstation_metadata
    5    chromatogram_spectra
    6          sample_tracker
    7            st_temp_join

    """

    # add original st shape then each filter to show reduction in size..

    logger.info(
        "Fetching CUPRAC wine data via joins of st-ct, then st-ct-ch_m, then st-ct-ch_m-ch_d.."
    )

    logger.info(f"st has shape: {con.sql('SELECT * FROM c_sample_tracker').df().shape}")

    st_cuprac = con.sql(
        """--sql
                        CREATE OR REPLACE TEMPORARY TABLE
                        st_cuprac
                        AS
                        SELECT *
                        FROM
                        c_sample_tracker
                        WHERE
                        detection='cuprac';
                        SELECT * FROM st_cuprac
                        """
    ).df()
    logger.info(f"After filtering for CUPRAC wines, st has shape: {st_cuprac.shape}")

    logger.info("joinng st to ct..")
    logger.info(f"ct shape: {con.sql('SELECT * FROM c_cellar_tracker').df().shape}..")

    """
    ## sample_tracker columns

    Index(['detection', 'sampler', 'samplecode', 'vintage', 'name', 'open_date','sampled_date', 'added_to_cellartracker', 'notes', 'size' 'ct_wine_name'],

    ## c_sample_tracker shape

    (190, 11), (179,11) when filtering for 'added' wines
    
    ## cellar_tracker_columns

    Index(['size', 'vintage', 'name', 'locale', 'country', 'region', 'subregion','appellation', 'producer', 'type', 'color', 'category', 'varietal',
       'wine'],
       
    ## c_cellar_tracker shape

    (145, 14)
    """

    # join st to ct
    st_ct_temp = con.sql(
        """--sql
        CREATE OR REPLACE TEMPORARY TABLE
        st_ct_temp
        AS
        SELECT
        st.detection, st.samplecode, ct.wine, ct.color, ct.varietal
        FROM
        st_cuprac st
        INNER JOIN
        c_cellar_tracker ct
        ON
        st.ct_wine_name = ct.wine
        WHERE
        ct.color='red';
        SELECT * FROM st_ct_temp;
    """
    ).pl()

    logger.info(
        f"After st-ct inner join of red wines, the resulting table has shape: {st_ct_temp.shape}.."
    )

    """
    ## st_ct_join shape

    (179, 25)
    """

    # join st_ct_join to metadata tbl. Need to do a left join on st_ct_temp to select the samples that we've already filtered for i.e. by detection method.

    """
    ## c_chemstation_metadata columns

    Index(['path', 'ch_samplecode', 'acq_date', 'acq_method', 'unit', 'signal',
       'vendor', 'seq_name', 'seq_desc', 'vialnum', 'originalfilepath', 'id',
       'desc', 'join_samplecode'],
      dtype='object')

    ## c_chemstation_metadata shape

    (175, 14)
    """
    logger.info(f"Now joining st-ct to ch_m..")
    logger.info(
        "before join, ch_m has"
        f" shape: {con.sql('SELECT * FROM c_chemstation_metadata').df().shape}.."
    )

    ch_m_st_ct_temp = con.sql(
        """--sql
        CREATE OR REPLACE TEMPORARY TABLE
        ch_m_st_ct_temp
        AS
        SELECT
        t.detection, t.samplecode, t.wine, t.color, t.varietal, chm.id
        FROM
        st_ct_temp t
        LEFT JOIN
        c_chemstation_metadata chm
        ON
        (
        chm.join_samplecode=t.samplecode
        );
        """
    )

    """
    ## ch_m_st_ct_temp shape
            
    (66, 6)
    """
    logger.info(
        "after st-ct join to ch_m, resulting table has shape:"
        f" {con.sql('SELECT * FROM ch_m_st_ct_temp;').pl().shape}.."
    )

    # ch_m_st_ct_ch_d

    logger.info("joining ch_m-st_ct_temp and ch_d..")

    # cs columns: id, mins, wavelength, value
    wine_data = con.sql(
        """--sql
                        CREATE OR REPLACE TEMPORARY TABLE
                        wine_data
                        AS
                        SELECT
                        t.detection, t.samplecode, t.wine, t.color, t.varietal, t.id, cs.mins, cs.wavelength, cs.value
                        FROM
                        ch_m_st_ct_temp t
                        LEFT JOIN
                        chromatogram_spectra cs
                        ON
                        (
                            t.id=cs.id
                        )
                        WHERE
                        cs.wavelength=450
                        AND
                        cs.mins<30;
                        SELECT * FROM wine_data;
                        """
    ).df()

    logger.info(f"after join, wine_data has shape:{wine_data.shape}..")
    logger.info(
        f"after join, wine_data has na in the following:\n{wine_data.isna().sum()}.."
    )

    return wine_data


@timeit
def pivot_wine_data(df):
    """
    Pivot wine_data on wines to produce a wide df with columns labeled with wine names
    and consisting of absorbance values.

    """
    logger.info("pivoting wine_data..")
    logger.info(f"before pivot, shape: {df.shape}")
    out_df = (
        df.loc[:, ["id", "samplecode", "wine", "value"]]
        .assign(i=lambda df: df.groupby(["id"]).cumcount())
        .assign(id_wine=lambda df: df["samplecode"] + "_-" + df["wine"])
        .pivot(columns="id_wine", values="value", index="i")
    )
    logger.info(f"after pivot, shape: {out_df.shape}..")
    logger.info(f"{out_df.isna().sum()}")
    logger.info(f"\n{out_df}")

    return out_df


def plot_wine_data(df):
    fig, pivoted_data_ax = plt.subplots(1)
    sns.lineplot(data=df)
    fig.suptitle("pivoted data")
    pivoted_data_ax.legend(bbox_to_anchor=(0.5, -0.15), loc="upper center")
    fig.show()


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
    model = pca.fit_transform(df.values)
    PC1 = model[:, 0]
    PC2 = model[:, 1]
    ldngs = pca.components_
    scalePC1 = PC1 / (PC1.max() - PC1.min())
    scalePC2 = PC2 / (PC2.max() - PC2.min())
    features = df.columns.tolist()

    make_biplot(features=features, ldngs=ldngs, scalePC1=scalePC1, scalePC2=scalePC2)


def main():
    con = db.connect(definitions.DB_PATH)
    wine_data = get_wine_data(con)
    pwine_data = pivot_wine_data(wine_data)
    build_model(pwine_data)


if __name__ == "__main__":
    main()
