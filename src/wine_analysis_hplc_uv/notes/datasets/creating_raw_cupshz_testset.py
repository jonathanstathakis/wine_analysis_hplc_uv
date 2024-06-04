"""
Refer to section [Creation of 'Raw' Dataset](./chapter_signal_preprocessing.ipynb) for context.
"""

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.get_test_data import gd
from wine_analysis_hplc_uv.old_signal_processing.signal_processor import (
    SignalProcessor,
)
import pandas as pd

sigpro = SignalProcessor()
df = gd()

# setup
df = (
    df.pipe(sigpro.long_format)
    .pipe(
        lambda df: (
            df.drop(["id", "detection"], axis=1)
            if pd.Series(["id", "detection"]).isin(df.columns).all()
            else df
        )
    )
    .pipe(sigpro.tidy_format)
    .drop(["163", "165", "ca0301"], axis=1)  # bad samples
)

df.to_parquet(definitions.RAW_PARQ_PATH)
