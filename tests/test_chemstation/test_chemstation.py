"""

"""
import pytest
import sys
from wine_analysis_hplc_uv.df_methods import df_methods
import os
from glob import glob
import random
import pandas as pd
import duckdb as db
from wine_analysis_hplc_uv.chemstation import read_single_file
import logging
from wine_analysis_hplc_uv.chemstation.chemstationprocessor import ChemstationProcessor

logger = logging.getLogger(__name__)


@pytest.fixture
def single_filepath():
    return "tests/test_data/agilent_D/139.D"


def test_read_single_file(single_filepath):
    """ """
    returndict = read_single_file.read_single_file(single_filepath)
    logger.info(returndict["metadata"])
    assert returndict


def test_metadata_df(chemstationprocessor):
    df_methods.test_df(chemstationprocessor.metadata_df)


# def test_metadata_df_to_csv(chemstationprocessor):
# chemstationprocessor.metadata_df.to_csv(os.path.join(os.getcwd(), "metadata_df.csv"))


def test_data_df(chemstationprocessor) -> None:
    # df_methods.describe_df(df=ch.data_df)

    groups = chemstationprocessor.data_df.groupby("id")
    group_shapes = [(name, group.shape) for name, group in groups]

    data_shape_df = pd.DataFrame(group_shapes, columns=["id", "shape"])
    data_shape_df = pd.merge(
        chemstationprocessor.metadata_df[["notebook", "id"]], data_shape_df, on="id"
    ).drop("id", axis=1)

    df_methods.test_df(chemstationprocessor.data_df)
    return None


def test_data_to_db(chemstationprocessor):
    """
    Write metadata and spectra data to a db table, test whether the input df's match the db table df's:
    - [ ] metadata
    - [ ] data
    """
    meta_tbl_name = "test_meta_tbl"
    spectra_tbl_name = "test_spectra_tbl"
    con = db.connect()
    chemstationprocessor.to_db(
        con=con,
        ch_metadata_tblname=meta_tbl_name,
        ch_sc_tblname=spectra_tbl_name,
    )

    db_metadata_df = con.sql(f"SELECT * FROM {meta_tbl_name}").df()
    db_data_df = con.sql(f"SELECT * FROM {spectra_tbl_name}").df()

    pd.testing.assert_frame_equal(
        chemstationprocessor.metadata_df, db_metadata_df, check_dtype=False
    )
    pd.testing.assert_frame_equal(
        chemstationprocessor.data_df, db_data_df, check_dtype=False
    )


def test_chemstationProcessor(datapaths):
    logging.debug(datapaths.sampleset)
    assert ChemstationProcessor(datapaths.sampleset)


# 2023-08-16 14:23:15 currently broken as have moved dup test method somewhere else, need to fix call
# def test_dup_key_test(chemstationprocessor):
#     metadata_df = chemstationprocessor.metadata_df
#     raw_dups = chemstationprocessor.test_dup_ids(metadata_df)
#     assert not raw_dups  # no duplicates before modification

#     def dup_random_id(df):
#         import random

#         i1, i2 = random.sample(df.index.tolist(), 2)

#         df.loc[i1, "id"] = df.loc[i2, "id"]

#         test_logger.debug(
#             f"swap hash keys: {df.loc[i1, 'notebook']} with {df.loc[i2, 'notebook']}"
#         )
#         return df

#     dup_hash_df = dup_random_id(metadata_df)

#     mod_dups = chemstationprocessor.test_dup_ids(dup_hash_df)

#     assert mod_dups  # assert that duplicates have now been added in


def get_src_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/"


def get_dst_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/"
