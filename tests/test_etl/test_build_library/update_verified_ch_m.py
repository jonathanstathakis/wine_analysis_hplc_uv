import logging
from tests.conftest import DataForTests
import pandas as pd
from wine_analysis_hplc_uv.etl.build_library.chemstation.chemstationprocessor import (
    ChemstationProcessor,
)

logger = logging.getLogger(__name__)


def update_verified_ch_m() -> None:
    """
    Run to update the csv containing the raw 'metadata df', a table containing metadata
    information parsed from agilent files. This file is used to test ChemstationProcessor,
    specifically tests.test_etl.test_build_library.test_ch_to_db.test_chpro_ch_m
    """

    # initialise a ChemstationProcessor on the input dataset path
    cp = ChemstationProcessor(lib_path=DataForTests.SAMPLESET)

    # Get new df
    new_df: pd.DataFrame = cp.metadata_df

    # get out filepath
    outpath = DataForTests.VERIFIED_CH_M

    # write new dataframe to filepath
    new_df.to_csv(outpath, mode="x", index=False)

    # report output
    logger.info(f"new metadata df written to {outpath}")


if __name__ == "__main__":
    logging.basicConfig()
    update_verified_ch_m()
