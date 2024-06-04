import pandas as pd
import polars as pl
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods.standardize_time import (
    _resample,
)
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods.standardize_time import (
    _methods,
)


def time_std_pipe(
    df: pd.DataFrame,
    time_col: str,
    val_col: str,
    group_col: str | list[str],
    label_cols: list[str],
    precision: int,
) -> pl.DataFrame:
    """
    Take a tidy format df of column levels ['samplecode','wine','vars'] and vars
    of ['mins','value'] with 'i' index and return a df of same format but 'mins'
    as global index of datatype `pd.TimeDelta`, rounded to millisecond and resampled
    to mean sampling frequency.

    Refer to
    'notebooks/time_axis_characterisation_and_normalization.ipynb' and
    'notebooks/downsampling_signals.ipynb'.

    It has been determined that the minimum level of precision that ensures that each
    time axis value is unique is a millisecond scale, thus after datatype conversion
    the mins columns are rounded to "L". Next the 0 element time offset is corrected so
    element zero = 0 mins. then the dataset is moved to a universal time index as
    these modifications should have made them all equal.

    Test by asserting the geometry changes as expected.
    """

    # store to test the transformation later

    df_ = _methods.from_multiindex_col_to_long_df(df=df)
    df_ = _methods.set_df_dtypes(df=df_)
    df_ = _methods.correct_float_error(df=df_, time_col=time_col, precision=precision)
    df_ = _methods.correct_zero_offset(df=df_)
    # df_ = pl.from_pandas(df_)
    df_ = _resample.resample_to_mean_freq(
        df=df_,
        time_col=time_col,
        group_col=group_col,
        value_col=val_col,
        label_cols=label_cols,
    )

    return df_
