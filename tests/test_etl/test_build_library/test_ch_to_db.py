"""
Tests for chemstation to db processes, raw and clean.
"""

from wine_analysis_hplc_uv.etl.build_library.chemstation.chemstationprocessor import (
    ChemstationProcessor,
)
import logging
from glob import glob

import pandas as pd
import pytest
from wine_analysis_hplc_uv.etl.build_library.chemstation.chemstation_methods import (
    uv_filepaths_to_list,
)

logger = logging.getLogger(__name__)


def test_verified_ch_m_csv(verified_ch_m):
    """
    test that the verified chemstation metadata csv file is read correctly
    """

    assert isinstance(verified_ch_m, pd.DataFrame)
    assert not verified_ch_m.empty


def test_verified_ch_d(verified_ch_d):
    """
    test that the verified chemstation data csv file is read correctly
    """
    assert isinstance(verified_ch_d, pd.DataFrame)
    assert not verified_ch_d.empty


@pytest.fixture
def uv_path_list(datapaths):
    """
    return the result of `uv_filepaths_to_list`
    """
    return uv_filepaths_to_list(datapaths.SAMPLESET)


def test_uv_filepaths_to_list(uv_path_list, datapaths):
    """
    check the dir to list assembler works, test data lib dir currently has 5 dirs in it so list should have length 5
    """
    assert (
        len(uv_path_list) == 5
    ), f",{datapaths.sampleset} globlist: {list(glob(datapaths.sampleset))}"


def test_chpro_ch_m(
    chemstationprocessor: ChemstationProcessor, verified_ch_m: pd.DataFrame
):
    """
    check that chemstations metadata dataframe has initialized correctly

    TODO: write script to update the test data file, as it is out of date.
    """
    ch_m = chemstationprocessor.metadata_df

    assert chemstationprocessor
    assert isinstance(ch_m, pd.DataFrame)
    assert not ch_m.empty

    pd.testing.assert_frame_equal(
        ch_m.astype({"Injection Volume": float}), verified_ch_m.infer_objects()
    )
