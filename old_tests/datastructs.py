import pytest
import pandas as pd


@pytest.fixture(scope="package")
def get_df():
    return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
