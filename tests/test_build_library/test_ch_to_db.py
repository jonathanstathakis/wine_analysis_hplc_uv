"""
Tests for chemstation to db processes, raw and clean.
"""
import duckdb as db
from wine_analysis_hplc_uv.core import ch_to_db
import os
from wine_analysis_hplc_uv import definitions
import logging
import pytest
import pandas as pd

logging.basicConfig()
testlogger = logging.getLogger(__name__)
testlogger.setLevel("INFO")
from wine_analysis_hplc_uv.chemstation import logger as chemlogger
from glob import glob
from wine_analysis_hplc_uv.chemstation.chemstation_methods import uv_filepaths_to_list

chemlogger.setLevel("INFO")


def test_verified_ch_m_csv(verified_ch_m, caplog):
    # test that the verified chemstation metadata csv file is read correctly
    assert isinstance(verified_ch_m, pd.DataFrame)
    assert not verified_ch_m.empty


def test_verified_ch_d(verified_ch_d):
    # test that the verified chemstation data csv file is read correctly
    assert isinstance(verified_ch_d, pd.DataFrame)
    print("HERE")
    testlogger.info("@@THIS IS A LOG MSG@@")
    assert not verified_ch_d.empty


@pytest.fixture
def uv_path_list(ch_data_path):
    return uv_filepaths_to_list(ch_data_path)


def test_uv_filepaths_to_list(uv_path_list, ch_data_path):
    # check the dir to list assembler works, test data lib dir currently has 5 dirs in it so list should have length 5
    assert (
        len(uv_path_list) == 5
    ), f",{ch_data_path} globlist: {list(glob(ch_data_path))}"


def test_chpro_ch_m(chemstationprocessor, verified_ch_m):
    ch_m = chemstationprocessor.metadata_df
    assert chemstationprocessor
    assert isinstance(ch_m, pd.DataFrame)
    assert not ch_m.empty
    pd.options.display.max_colwidth = 20
    pd.testing.assert_frame_equal(ch_m, verified_ch_m)


def test_chpro_ch_m(chemstationprocessor, verified_ch_d):
    ch_d = chemstationprocessor.data_df
    assert chemstationprocessor
    assert isinstance(ch_d, pd.DataFrame)
    assert not ch_d.empty
    pd.options.display.max_colwidth = 20
    pd.testing.assert_frame_equal(ch_d, verified_ch_d)


if __name__ == "__main__":
    test_ch_to_db()