"""
contains tests for `chapter_one.polars_extension` module
"""

import polars as pl
from wine_analysis_hplc_uv.chapter_one import polars_extension
import pytest


@pytest.fixture
def sample_df() -> pl.DataFrame:
    return pl.DataFrame(
        {"int_cat_col_unordered": [1, 2, 5, 4, 3], "str_cat_col": ["a", "b", "c"]},
        schema={"int_cat_col_unordered": int, "str_cat_col": str},
    )


def test_to_enum(sample_df: pl.DataFrame) -> None:
    """
    test if `polars_extension.to_enum` converts an unordered int column to a categorical column with numerically ordered categories, and also a string column to a categorical column.
    """
    polars_extension.to_enum(sample_df, "int_cat_col_unordered")

    # TODO: finish this test, write another one for the auc calculations, finish refactoring the notebook
