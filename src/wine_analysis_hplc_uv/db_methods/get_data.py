from mydevtools.function_timer import timeit
import logging
import pandas as pd
import polars as pl

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


@timeit
def get_wine_data(
    con,
    detection: tuple = (None,),
    samplecode: tuple = (None,),
    color: tuple = (None,),
    wavelength: tuple = (None,),
    varietal: tuple = (None,),
    wine: tuple = (None,),
    mins: tuple = (None, None),
):
    """
    Join the sample tracker and cellar tracker tables, then chemstation metadata then
    finally chemstation data table.

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

    Index(['detection', 'sampler', 'samplecode', 'vintage', 'name', 'open_date',
    'sampled_date', 'added_to_cellartracker', 'notes', 'size' 'ct_wine_name'],

    ## c_sample_tracker shape

    (190, 11), (179,11) when filtering for 'added' wines

    ## cellar_tracker_columns

    Index(['size', 'vintage', 'name', 'locale', 'country', 'region', 'subregion',
    'appellation', 'producer', 'type', 'color', 'category', 'varietal',
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

    assert isinstance(detection, tuple)
    assert isinstance(samplecode, tuple)
    assert isinstance(wine, tuple)
    assert isinstance(color, tuple)
    assert isinstance(varietal, tuple)
    assert isinstance(mins, tuple)
    assert isinstance(wavelength, tuple)

    # join st to ct
    con.execute(
        f"""--sql
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
          ((SELECT UNNEST($detection)) IS NULL
            OR st.detection IN (SELECT * FROM UNNEST($detection)))
            AND ((SELECT UNNEST($samplecode))
                IS NULL OR st.samplecode IN (SELECT * FROM UNNEST($samplecode)))
                AND st.samplecode NOT IN ('72','98')
            AND ((SELECT UNNEST($color)) IS NULL
                OR ct.color IN (SELECT * FROM UNNEST($color)))
            AND ((SELECT UNNEST($varietal)) IS NULL
                OR ct.varietal IN (SELECT * FROM UNNEST($varietal)))
            AND ((SELECT UNNEST($wine)) IS NULL
                OR ct.wine IN (SELECT * FROM UNNEST($wine)))
            AND ((SELECT UNNEST($wavelength)) IS NULL
                OR cs.wavelength IN (SELECT * FROM UNNEST($wavelength)))
            AND ($min_start IS NULL OR cs.mins >= $min_start)
            AND ($min_end IS NULL OR cs.mins <= $min_end)
        """,
        {
            "detection": detection,
            "samplecode": samplecode,
            "color": color,
            "varietal": varietal,
            "wine": wine,
            "wavelength": wavelength,
            "min_start": mins[0],
            "min_end": mins[1],
        },
    )
