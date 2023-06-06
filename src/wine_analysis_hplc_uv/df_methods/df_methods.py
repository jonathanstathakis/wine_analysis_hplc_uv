# spectrum_df['signal_shape'] = spectrum_df.apply(lambda row : row[wavelength].shape, axis = 1)
# spectrum_df['signal_index'] = spectrum_df.apply(lambda row : row[wavelength].index.tolist(), axis = 1)
# spectrum_df['signal_columns'] = spectrum_df.apply(lambda row : row[wavelength].columns.tolist(), axis = 1)

"""
Contains general df methods to improve quality of life when working with pandas dataframes.
"""

import pandas as pd


def describe_df(df: pd.DataFrame) -> None:
    print("df shape:", df.shape)
    print("df columns", df.columns)
    print("df index", df.index)

    return None


def test_df(df: pd.DataFrame) -> None:
    assert not df.empty, "DataFrame is empty"
    assert not df.isnull().values.any(), "DataFrame contains NaN values"
    assert (
        len(df.drop_duplicates()) > 1
    ), "DataFrame does not have more than one unique row"
    return None


def make_dtype_dict(df: pd.DataFrame, dtype: type = pd.StringDtype) -> dict:
    f"converting input df dtypes to {dtype}..\n"
    col_list = df.columns.tolist()
    datatype_list = [dtype] * len(col_list)
    zip_dict = dict(zip(col_list, datatype_list))

    return zip_dict
