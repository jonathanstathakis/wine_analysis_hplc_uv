import logging
import duckdb as db

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

from dataclasses import dataclass


@dataclass
class WineData:
    db_path: str

    def __post_init__(self):
        self.con = db.connect(database=self.db_path)

        self.get_wine_data_query_path: str = "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/db_methods/get_data_query.sql"

    def _get_wine_data_query_str(self):
        with open(self.get_wine_data_query_path, "r") as f:
            query_str = f.read()

        return query_str

    def get_wine_data(
        self,
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

        for var in [detection, samplecode, wine, color, varietal, mins, wavelength]:
            assert isinstance(var, tuple)

        # join st to ct
        self.con.execute(
            self._get_wine_data_query_str(),
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
