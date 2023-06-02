"""
Chemstation data process tests

"""
import os
from wine_analysis_hplc_uv.chemstation.chemstationprocessor import ChemstationProcessor
import pytest


@pytest.fixture
def datadirpath():
    return "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files"

    # return os.path.join(os.path.dirname(__file__), "testdata")


def datadirpath_():
    return os.path.join(os.path.dirname(__file__), "testdata")


def test_chemstation_process(datadirpath: str):
    chprocess = ChemstationProcessor(datadirpath)
    chprocess.cleanup_pickle()
    assert chprocess.datalibpath
    assert chprocess.fpathlist
    assert chprocess.pkfname
    assert chprocess.pkfpath
    assert chprocess.ch_data_dicts_tuple[0]
    assert chprocess.ch_data_dicts_tuple[1]
    assert not metadata_df.empty

    # make sure the pickle cleanup works after process
    assert not os.path.exists(chprocess.pkfpath)
    return None


# def test_ch_to_db(chprocess):
def test_process_to_csv(data_dir_path: str):
    chprocess = ChemstationProcessor(datadirpath())
    chprocess.cleanup_pickle()
    chprocess.to_csv()


def main():
    test_chemstation_process(datadirpath_())
    return None


if __name__ == "__main__":
    main()
