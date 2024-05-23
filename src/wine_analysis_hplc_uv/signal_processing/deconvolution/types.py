import polars as pl
import numpy as np
import numpy.typing as npt

type SkewNormParams2Peaks = pl.DataFrame
type P0Tbl = pl.DataFrame
type LBTbl = pl.DataFrame
type UBTbl = pl.DataFrame
type ParamTbl = pl.DataFrame

# use as an alias for 1D numpy float arrays
type FloatArray = npt.NDArray[np.float64]

# a mapping of parameters to values
type PeakParamDict = dict[str, float]

# a mapping of peak labels to parameter dicts
type ParamDict = dict[str, PeakParamDict]

type DataDict = dict[str, FloatArray]
