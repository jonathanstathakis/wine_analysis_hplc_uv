"""
2023-06-07 22:35:30

Second iteration of build_library.py, integrating the new behaviors defined by the various classes handling the imported data.
- [ ] sampletracker to db
- [ ] cellar tracker to db
- [ ] chemstation to db

sampletracker amd cellartracker wine names need to be the same, as that is their join key.

sampletracker and chemstation_metadata ids need to match as that is their join key.
"""
import os
from mydevtools import project_settings
from rainbow.agilent import chemstation
from wine_analysis_hplc_uv.chemstation.chemstationprocessor import ChemstationProcessor
from wine_analysis_hplc_uv.sampletracker.sample_tracker_processor import SampleTracker
from wine_analysis_hplc_uv.cellartracker_methods.my_cellartracker_class import (
    MyCellarTracker,
)


def build_biblioteca_nueva():
    """
    2023-06-07 22:58:05 A rehash of the previous build_library as per module docstring.
    """
    chemstation_to_db()
    return None


def get_data_lib_path():
    return os.environ.get("DATA_LIB_PATH")


def chemstation_to_db(data_lib_path=get_data_lib_path()):
    chemstation = ChemstationProcessor(datalibpath=data_lib_path, usepickle=False)


def main():
    build_biblioteca_nueva()
    return None


if __name__ == "__main__":
    main()
