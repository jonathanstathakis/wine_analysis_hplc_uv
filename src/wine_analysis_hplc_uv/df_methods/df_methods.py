# spectrum_df['signal_shape'] = spectrum_df.apply(lambda row : row[wavelength].shape, axis = 1)
# spectrum_df['signal_index'] = spectrum_df.apply(lambda row : row[wavelength].index.tolist(), axis = 1)
# spectrum_df['signal_columns'] = spectrum_df.apply(lambda row : row[wavelength].columns.tolist(), axis = 1)

"""
Contains general df methods to improve quality of life when working with pandas dataframes.
"""

import pandas as pd


def describe_df(df: pd.DataFrame) -> None:
    print(f"df size: {df.size:,}")
    print(f"df shape: {df.shape}")
    if len(df.columns) < 10:
        print(f"df column labels: {df.columns}")
    else:
        print(f"first 10 column labels:{df.columns[:10]}")
    print(f"df index labels:, {df.index}")
    if len(df.index) < 10:
        print(f"df index labels: {df.index}")
    else:
        print(f"first 10 indexes: {df.index[:10]}")

    isna_tot = df.isna().sum().sum()

    print(f"df total na count: {isna_tot:,}")

    isna_ratio = isna_tot / df.size

    print(f"ratio of nas:{round(isna_ratio, 2):,}")

    def sum_na_by_col(df):
        na_sum_series = df.isna().sum()
        na_sum_series = na_sum_series[na_sum_series > 0]

        print(f"df na count by column {na_sum_series}")

    sum_na_by_col(df)
    print(df.head(3))

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
