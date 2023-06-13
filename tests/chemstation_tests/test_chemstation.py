"""

"""
from importlib import metadata
import traceback
import sys
from wine_analysis_hplc_uv.chemstation.chemstation_to_db_methods import (
    chromatogram_spectra_to_db,
)
from wine_analysis_hplc_uv.chemstation.process_outputs.output_to_csv import (
    metadata_to_csv,
)

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")
from mytestmethods.mytestmethods import test_report
from wine_analysis_hplc_uv.chemstation import chemstationprocessor
from wine_analysis_hplc_uv.df_methods import df_methods
from wine_analysis_hplc_uv.definitions import LIB_DIR
from make_test_sample_dir import create_test_pool
from chemstation_tests import (
    chemstation_logger,
    test_logger,
)
import os
from glob import glob
import random
import shutil
import pandas as pd


import duckdb as db


def test_chemstation():
    src_dir = get_src_path()
    dst_dir = get_dst_path()
    create_test_pool(src_dir=src_dir, dst_parent_dir=dst_dir)

    path = get_dst_path()
    # libpath = LIB_DIR
    try:
        test_logger.info("generating CH object..")
        ch = chemstationprocessor.ChemstationProcessor(lib_path=path, usepickle=False)
        test_logger.info("CH object generated.")
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        shutil.rmtree(dst_dir)  # clean up sample pool after testing is complete

    tests = [
        (test_ChemstationProcessor_init, ch),
        (test_metadata_df, ch),
        (test_data_df, ch),
        (test_dup_key_test, ch),
        # (test_data_to_db, ch),
    ]
    test_report(tests)
    shutil.rmtree(dst_dir)  # clean up sample pool after testing is complete
    return None


def test_ChemstationProcessor_init(ch):
    assert ch


def test_metadata_df(ch):
    df_methods.test_df(ch.metadata_df)


def test_data_df(ch) -> None:
    # df_methods.describe_df(df=ch.data_df)
    groups = ch.data_df.groupby("hash_key")
    group_shapes = [(name, group.shape) for name, group in groups]
    print("")

    data_shape_df = pd.DataFrame(group_shapes, columns=["hash_key", "shape"])
    data_shape_df = pd.merge(
        ch.metadata_df[["notebook", "hash_key"]], data_shape_df, on="hash_key"
    ).drop("hash_key", axis=1)
    print(data_shape_df)

    df_methods.test_df(ch.data_df)


def get_db_filepath():
    return os.path.join(os.getcwd(), "test_ch.db")


def test_data_to_db(ch):
    """
    Write metadata and spectra data to a db table, test whether the input df's match the db table df's:
    - [ ] metadata
    - [ ] data
    """
    db_filepath = get_db_filepath()
    meta_tbl_name = "test_meta_tbl"
    spectra_tbl_name = "test_spectra_tbl"

    ch.to_db(
        db_filepath=db_filepath,
        ch_metadata_tblname=meta_tbl_name,
        ch_sc_tblname=spectra_tbl_name,
    )

    db_metadata_df = None
    db_data_df = None

    with db.connect(db_filepath) as con:
        db_metadata_df = con.sql(f"SELECT * FROM {meta_tbl_name}").df()
        db_data_df = con.sql(f"SELECT * FROM {spectra_tbl_name}").df()

    pd.testing.assert_frame_equal(ch.metadata_df, db_metadata_df)
    pd.testing.assert_frame_equal(ch.data_df, db_data_df)

    os.remove(db_filepath)  # cleanup


def test_dup_key_test(ch):
    metadata_df = ch.metadata_df
    raw_dups = chemstationprocessor.test_dup_hash_keys(metadata_df)
    assert not raw_dups  # no duplicates before modification

    def dup_random_hash_key(df):
        import random

        i1, i2 = random.sample(df.index.tolist(), 2)

        df.loc[i1, "hash_key"] = df.loc[i2, "hash_key"]

        test_logger.debug(
            f"swap hash keys: {df.loc[i1, 'notebook']} with {df.loc[i2, 'notebook']}"
        )
        return df

    dup_hash_df = dup_random_hash_key(metadata_df)

    mod_dups = chemstationprocessor.test_dup_hash_keys(dup_hash_df)

    assert mod_dups  # assert that duplicates have now been added in


def get_src_path():
    return "/Users/jonathan/0_jono_data/mres_data_library/"


def get_dst_path():
    return "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_data/"


def main():
    test_chemstation()
    return None


if __name__ == "__main__":
    main()
