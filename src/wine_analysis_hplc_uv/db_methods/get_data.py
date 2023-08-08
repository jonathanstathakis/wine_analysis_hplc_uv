from mydevtools.function_timer import timeit
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


@timeit
def get_wine_data(
    con,
    detection=None,
    samplecode=None,
    color=None,
    wavelength=None,
    varietal=None,
    wine=None,
    mins: tuple = (None, None),
):
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

    # join st to ct
    con.execute(
        """--sql
        CREATE OR REPLACE TEMPORARY TABLE wine_data AS
        SELECT st.detection,
            st.samplecode,
            ct.wine,
            ct.color,
            ct.varietal,
            chm.id,
            cs.mins,
            cs.wavelength,
            cs.value
        FROM c_sample_tracker st
            INNER JOIN c_cellar_tracker ct ON st.ct_wine_name = ct.wine
            LEFT JOIN c_chemstation_metadata chm ON (
                chm.join_samplecode = st.samplecode
            )
            LEFT JOIN chromatogram_spectra cs ON (chm.id = cs.id)
        WHERE
            st.detection = COALESCE($detection, st.detection)
            AND st.samplecode =  COALESCE($samplecode, st.samplecode)
            AND ct.color= COALESCE($color, ct.color)
            AND ct.varietal= COALESCE($varietal, ct.varietal)
            AND ct.wine=COALESCE($wine, ct.wine)
            AND cs.wavelength = COALESCE($wavelength, cs.
            wavelength)
            AND cs.mins >= COALESCE($min_start, cs.mins)
            AND cs.mins <= COALESCE($min_end, cs.mins)
        """,
        {
            "detection": detection,
            "samplecode": samplecode,
            "color": color,
            "varietal": varietal,
            "wavelength": wavelength,
            "wine": wine,
            "min_start": mins[0],
            "min_end": mins[1],
        },
    )


def main():
    logger.info("beginning main..")
    from wine_analysis_hplc_uv import definitions
    import duckdb as db

    con = db.connect(definitions.DB_PATH)
    get_wine_data(con)


if __name__ == "__main__":
    main()
