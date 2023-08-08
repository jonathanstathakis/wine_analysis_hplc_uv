from mydevtools.function_timer import timeit
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


@timeit
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

    ## sample_tracker columns

    Index(['detection', 'sampler', 'samplecode', 'vintage', 'name', 'open_date','sampled_date', 'added_to_cellartracker', 'notes', 'size' 'ct_wine_name'],

    ## c_sample_tracker shape

    (190, 11), (179,11) when filtering for 'added' wines

    ## cellar_tracker_columns

    Index(['size', 'vintage', 'name', 'locale', 'country', 'region', 'subregion','appellation', 'producer', 'type', 'color', 'category', 'varietal',
       'wine'],

    ## c_cellar_tracker shape

    (145, 14)

    ## st_ct_join shape

    (179, 25)

    ## c_chemstation_metadata columns

    Index(['path', 'ch_samplecode', 'acq_date', 'acq_method', 'unit', 'signal',
       'vendor', 'seq_name', 'seq_desc', 'vialnum', 'originalfilepath', 'id',
       'desc', 'join_samplecode'],
      dtype='object')

    ## c_chemstation_metadata shape

    (175, 14)

    ## ch_m_st_ct_temp shape

    (66, 6)
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
                        detection='cuprac'
                        ;
                        SELECT * FROM st_cuprac
                        """
    ).df()
    logger.info(f"After filtering for CUPRAC wines, st has shape: {st_cuprac.shape}")

    logger.info("joinng st to ct..")
    logger.info(f"ct shape: {con.sql('SELECT * FROM c_cellar_tracker').df().shape}..")

    """
    
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
        ct.color='red'
        ;
        SELECT * FROM st_ct_temp;
    """
    ).pl()

    logger.info(
        f"After st-ct inner join of red wines, the resulting table has shape: {st_ct_temp.shape}.."
    )

    # join st_ct_join to metadata tbl. Need to do a left join on st_ct_temp to select the samples that we've already filtered for i.e. by detection method.

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
        cs.mins<30
        ;
        SELECT * FROM wine_data;
        """
    ).pl()

    logger.info(f"after join, wine_data has shape:{wine_data.shape}..")
    # logger.info(
    #     f"after join, wine_data has na in the following:\n{wine_data.isna().sum()}.."
    # )

    return wine_data


def main():
    logger.info("beginning main..")
    from wine_analysis_hplc_uv import definitions
    import duckdb as db

    con = db.connect(definitions.DB_PATH)
    get_wine_data(con)


if __name__ == "__main__":
    main()
