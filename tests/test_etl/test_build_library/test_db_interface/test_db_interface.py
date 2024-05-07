from typing import Literal
import pytest

from wine_analysis_hplc_uv.notebooks.peak_deconv import db_interface

from seaborn import load_dataset
from wine_analysis_hplc_uv.notebooks.peak_deconv.db_interface import DBInterface

import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def dbint(testdbpath: Literal[":memory:"]):
    return db_interface.DBInterface(testdbpath)


@pytest.fixture
def penguins():
    return load_dataset("penguins")


@pytest.fixture
def testtblname():
    return "testtbl"


def test_init(dbint: DBInterface):
    assert dbint


def test_insert_df_into_tbl(
    dbint: DBInterface, penguins, testtblname: Literal["testtbl"]
):
    # 1. check creation if it doesnt exist

    # first check the table doesnt exist, fail if it does

    assert not dbint._checkexists(testtblname)

    dbint.insert_df_into_tbl(df=penguins, tblname=testtblname)

    assert dbint._checkexists(testtblname)

    # 2. now that a table has been added, insert into it and check that the lengths have changed.

    length_1 = dbint._get_rowcount(testtblname)

    dbint.insert_df_into_tbl(df=penguins, tblname=testtblname)

    length_2 = dbint._get_rowcount(testtblname)

    # length 2 should be larger than length 1

    from io import StringIO

    buf = StringIO()
    length_1.info(buf=buf)

    logger.info(buf.getvalue())

    logger.info(length_1.numrows)

    assert length_2.numrows.iloc[0] > length_1.numrows.iloc[0]


def test_drop_tbl(dbint, penguins, testtblname):
    # first create a table, check its existance, then drop and check its nonexistance

    dbint.insert_df_into_tbl(df=penguins, tblname=testtblname)

    assert dbint._checkexists(testtblname)

    dbint.drop_tbl(testtblname)

    assert not dbint._checkexists(testtblname)
