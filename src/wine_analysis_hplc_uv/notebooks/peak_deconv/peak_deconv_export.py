"""
2023-11-20 10:09:45

This module will contain a method to export the output of peak deconvolution to a DB
table. Specifically, it will handle chunkwise insertion, as this process will both be
slow and iterative as we develop better deconvolution methods.
"""

import duckdb as db
import pandas as pd
import numpy as np
from seaborn import objects as so
from wine_analysis_hplc_uv import definitions

# from
