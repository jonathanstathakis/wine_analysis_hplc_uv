"""
A file to contain all the general data treatment methods: baseline correction, mean centering, normalization, peak alignment, peak finding, etc.
"""
import numpy as np
import pandas as pd
from pybaselines import Baseline
from scipy.signal import find_peaks
from typing import Any


def calc_baseline(signal_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create baseline obj then fit the baseline on it. return baseline as df of ['mins','input_colname']
    """
    input_signal_time_axis_colname: str = list(signal_df.columns)[0]
    input_signal_y_axis_colname: str = list(signal_df.columns)[1]

    output_signal_axis_colname: str = "baseline"

    baseline_obj: Baseline = Baseline(signal_df[input_signal_time_axis_colname])
    baseline_y: tuple[Any, dict[str, Any]] = baseline_obj.iasls(
        signal_df[input_signal_y_axis_colname]
    )[0]
    baseline_df = signal_df[[input_signal_time_axis_colname]].copy(deep=True)
    baseline_df[output_signal_axis_colname] = baseline_y
    return baseline_df


def baseline_area(df: pd.DataFrame) -> float:
    """
    calculate area under the baseline curve
    """
    area = np.trapz(y=df["mAU"], x=df["mins"])
    return area


def peak_finder(
    x: pd.Series, y: pd.Series, in_height=None, in_prominence=None
) -> pd.DataFrame:
    """
    takes two pd.Series, x and y, finds the peaks in the y array and returns a peak df of shape ['peak_x', 'peak_y'].

    Note: find_peaks returns a tuple of.. something. the first element is the found peaks idx in the supplied 1D array.

    Even though the find_peaks code refers to the 1D array as x, I will refer to it as y to maintain consistancy with the higher level code.
    """
    peak_idx, _ = find_peaks(y, height=5, prominence=5)

    peak_x, peak_y = x[peak_idx], y[peak_idx]

    peak_df = pd.DataFrame({"peak_x": peak_x, "peak_y": peak_y})

    return peak_df


from typing import List, Union

import pandas as pd


def subset_spectra(
    df_series: pd.DataFrame, wavelength: Union[str, List[str]] = None
) -> pd.DataFrame:
    """
    Given a dataframe of mins | nm_1 | ... | nm_n, subset to return a df of same length but only the specified wavelengths. A single wavelength can be selected by providing a single string to 'wavelength'.
    """
    if wavelength == None:
        print("No wavelength values provided, therefore no point using this function.")
        raise RuntimeError

    def get_wavelength(spectrum_df: pd.DataFrame, wavelength_input) -> pd.DataFrame:
        # If wavelength_input is a single string, convert it to a list with one element
        if isinstance(wavelength_input, str):
            wavelength_input = [wavelength_input]

        spectrum_df = spectrum_df.set_index("mins")
        single_wavelength_df = spectrum_df[wavelength_input].copy()
        single_wavelength_df = single_wavelength_df.reset_index()

        return single_wavelength_df

    subset_spectra_series = pd.Series(
        df_series.apply(lambda row: get_wavelength(row, wavelength)),
        index=df_series.index,
    )

    return subset_spectra_series


def subtract_baseline_from_spectra(df: pd.DataFrame) -> pd.DataFrame:
    """
    Subtract baseline from each column of a spectrum  as a pandas dataframe of column format RangeIndex | mins | wavelength_1, .. , wavelength_n.

    Only pass in mins and the wavelength columns.
    """

    def check_non_numeric_columns(df):
        non_numeric_columns = ~df.dtypes.apply(pd.api.types.is_numeric_dtype)
        if non_numeric_columns.any():
            non_numeric_column_names = df.columns[non_numeric_columns].tolist()
            raise ValueError(
                "\nError: dataframe with non-numeric columns passed to"
                " subtract_baseline_from_spectra(). Non-numeric columns:"
                f" {non_numeric_column_names}\n"
            )

    try:
        check_non_numeric_columns(df)
    except ValueError as e:
        print(e)

    baseline_obj = Baseline(df["mins"])
    baseline_df = df.apply(lambda spectrum_col: baseline_obj.iasls(spectrum_col)[0])
    baseline_subtracted_spectra_df = df - baseline_df

    return baseline_subtracted_spectra_df


def test_baseline_correction():
    import duckdb as db

    con = db.connect("wine_auth_db.db")

    query_1 = """
    SELECT A.*,
        sub_query.name_ct
    FROM
        spectrums A
    JOIN (
        SELECT
            hash_key,
            name_ct
        FROM
            super_table
        LIMIT
        1    
    ) sub_query
    ON
        A.hash_key = sub_query.hash_key;
    """

    spectra_df = con.sql(query_1).df()
    names = spectra_df["name_ct"]
    baseline_subtracted_df = subtract_baseline_from_spectra(
        spectra_df.drop(["hash_key", "name_ct"], axis=1)
    )
    baseline_subtracted_df["name_ct"] = names


def normalize_library_absorbance(series: pd.Series) -> pd.Series:
    """
    Normalise a series of dataframes consisting of numeric values across the entire series, i.e. relative to each other. Returns a normalized series of dataframes.

    Make sure to remove mins from
    """

    def check_numeric_dataframes(series: pd.Series) -> bool:
        for df in series:
            non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_columns) > 0:
                return False
        return True

    if not check_numeric_dataframes(series):
        raise ValueError(
            "All DataFrames in the series must consist of numeric values only."
        )

    # Find the global minimum and maximum values
    # assuming column 0 is mins, remove from the transformation
    local_mins = series.apply(lambda df: df.iloc[:, 1:].min().min())
    local_maxs = series.apply(lambda df: df.iloc[:, 1:].max().max())

    global_min = local_mins.min()
    global_max = local_maxs.max()

    # Normalize each DataFrame in the series
    def normalize_y_axis(df: pd.DataFrame, global_min: float, global_max: float):
        norm_df = pd.DataFrame()
        norm_df["mins"] = df["mins"]
        df = df.iloc[:, 1:]
        norm_df["normalized_signal"] = (df - global_min) / (global_max - global_min)

        return norm_df

    normalized_series = series.apply(
        lambda df: normalize_y_axis(df, global_min, global_max)
    )

    normalized_series.name = "normalized"
    return normalized_series


def main():
    test_baseline_correction()


if __name__ == "__main__":
    main()
