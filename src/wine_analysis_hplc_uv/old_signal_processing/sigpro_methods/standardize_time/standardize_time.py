import pandas as pd
import polars as pl
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods.standardize_time._methods import (
    _resample,
)
from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods.standardize_time._methods._methods import (
    correct_float_error,
    correct_zero_offset,
    from_multiindex_col_to_long_df,
    set_df_dtypes,
)


def standardize_time(
    df: pd.DataFrame,
    time_col: str,
    group_col: str | list[str],
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

    df_ = from_multiindex_col_to_long_df(df=df)
    df_ = set_df_dtypes(df=df_)
    df_ = correct_float_error(df=df_, time_col=time_col, precision=precision)
    df_ = correct_zero_offset(df=df_)
    # df_ = pl.from_pandas(df_)
    df_ = _resample.resample_to_mean_freq(
        df=df_, time_col=time_col, group_col=group_col
    )

    # a rudimentary transformation test. As we are expecting the same number of rows
    # after the transformation, test that. We're also expecting the number of columns
    # to be halved as we move from intra-sample 'mins' columns to 1 mins index which
    # is replacing 'i'.

    return df_
