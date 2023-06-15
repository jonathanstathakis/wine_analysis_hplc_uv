import pandas as pd
import ch_m_id_cleaner
import ch_m_date_cleaner
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods


def ch_metadata_tbl_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    """
    driver function for cleaning chemstation metadata table to enable joins with sample_tracker table
    """

    df = (
        df.pipe(df_cleaning_methods.df_string_cleaner)
        .pipe(rename_chemstation_metadata_cols)
        .pipe(ch_m_date_cleaner.format_acq_date())
        .pipe(ch_m_id_cleaner.ch_m_id_cleaner)
        # .pipe(chemstation_metadata_drop_unwanted_runs)
    )

    return df


def rename_chemstation_metadata_cols(df):
    df = df.rename(
        {"notebook": "id", "date": "acq_date", "method": "acq_method"}, axis=1
    )
    return df
