""" """

import pytest
from tests.my_test_tools import pandas_tools
import pandas as pd
import duckdb as db
from wine_analysis_hplc_uv.etl.build_library.chemstation import read_single_file
import logging
from wine_analysis_hplc_uv.etl.build_library.chemstation.chemstationprocessor import (
    ChemstationProcessor,
)
from pathlib import Path
from tests.conftest import DataForTests

logger = logging.getLogger(__name__)


@pytest.fixture
def single_filepath():
    return str(Path(DataForTests.SAMPLESET) / "139.D")


def test_read_single_file(single_filepath):
    """ """
    returndict = read_single_file.read_single_file(single_filepath)
    logger.info(returndict["metadata"])
    assert returndict


def test_metadata_df(chemstationprocessor):
    pandas_tools.verify_df(chemstationprocessor.metadata_df)


# def test_metadata_df_to_csv(chemstationprocessor):
# chemstationprocessor.metadata_df.to_csv(os.path.join(os.getcwd(), "metadata_df.csv"))


def test_data_df(chemstationprocessor) -> None:
    groups = chemstationprocessor.data_df.groupby("id")
    group_shapes = [(name, group.shape) for name, group in groups]

    data_shape_df = pd.DataFrame(group_shapes, columns=["id", "shape"])
    data_shape_df = pd.merge(
        chemstationprocessor.metadata_df[["notebook", "id"]], data_shape_df, on="id"
    ).drop("id", axis=1)

    pandas_tools.verify_df(chemstationprocessor.data_df)
    return None


def test_data_to_db(
    chemstationprocessor,
    meta_tbl_name="test_meta_tbl",
    spectra_tbl_name="test_spectra_tbl",
    con=db.connect(),
):
    """
    Write metadata and spectra data to a db table, test whether the input df's match the db table df's
    """

    # write the tables to the database
    chemstationprocessor.to_db(
        con=con,
        ch_metadata_tblname=meta_tbl_name,
        ch_sc_tblname=spectra_tbl_name,
    )

    # retrieve the written tables from the database
    db_metadata_df = con.sql(f"SELECT * FROM {meta_tbl_name}").df()
    db_data_df = con.sql(f"SELECT * FROM {spectra_tbl_name}").df()

    # test the written table dataframes against the in-memory tables
    pd.testing.assert_frame_equal(
        chemstationprocessor.metadata_df, db_metadata_df, check_dtype=False
    )

    pd.testing.assert_frame_equal(
        chemstationprocessor.data_df.rename_axis(
            None, axis=1
        ),  # remove pandas in-memory specific metadata
        db_data_df,
        check_dtype=False,
    )


def test_chemstationProcessor():
    """
    Test whether ChemstationProcessor initializes without error on the sample set.
    """
    assert ChemstationProcessor(DataForTests.SAMPLESET)


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
