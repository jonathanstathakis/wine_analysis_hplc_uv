import random
import polars as pl
import numpy as np
from tests import constants
from wine_analysis_hplc_uv.signal_processing.deconvolution.types import (
    SkewNormParams2Peaks,
    FloatArray,
    LBTbl,
    UBTbl,
    P0Tbl,
    ParamDict,
)


def nested_dict_to_df(
    nested_dict: ParamDict, level_1_colname: str, level_2_colname: str
) -> pl.DataFrame:
    """
    convert a 2 level nested dict to a polars dataframe with the keys as label columns and the bottom level values as the value col.
    """
    dfs = []
    values = "values"
    for k, v in nested_dict.items():
        dfs.append(
            pl.DataFrame(
                data=[list(v.keys()), list(v.values())],
                schema=[level_2_colname, values],
            ).with_columns(pl.lit(k).alias(level_1_colname))
        )
    df = (
        pl.concat(dfs)
        .select([level_1_colname, level_2_colname, values])
        .sort([level_1_colname, level_2_colname])
    )

    return df


class CurveFitParamTbls:
    def __init__(self, input_tbl: pl.DataFrame, x: FloatArray):
        """
        container class of the test tables derived from an input parameter table.

        :param input_tbl: a table of 'peak','param','values' containing the skewnorm dist. pdf parameters used to generate the test data.

        The test attempts to recreate these parameters through the curve fit function using a randomized initial guess `p0` and lower and upper bounds based on the values of `input_tbl`.
        """
        self.x = x

        self.input_tbl = input_tbl.rename({"values": "actual"})
        self.ub = _gen_ub_tbl(param_tbl=self.input_tbl, x=x)
        self.lb = _gen_lb_tbl(param_tbl=self.input_tbl, x=x)
        self.p0 = _gen_p0_tbl(param_tbl=self.input_tbl)


def _gen_ub_tbl(param_tbl: SkewNormParams2Peaks, x: FloatArray) -> UBTbl:
    """
    For a dict of params calculate the lower bound
    """

    df = param_tbl.select(
        pl.col("peak"),
        pl.col('param'),
        pl.when(pl.col("param").eq("amp")).then(pl.col("actual").mul(10))
        .when(pl.col("param").eq("loc")).then(x[-1])
        .when(pl.col("param").eq("scale")).then(pl.col("actual").mul(2))
        .when(pl.col("param").eq("skew")).then(np.inf)
        .alias('ub')
    )  # fmt: skip

    return df


def _gen_lb_tbl(param_tbl: SkewNormParams2Peaks, x: FloatArray) -> LBTbl:
    """
    For a dict of params calculate the lower bound
    """

    df = param_tbl.select(
        pl.col("peak"),
        pl.col('param'),
        pl.when(pl.col("param").eq("amp")).then(pl.col("actual").mul(0.1))
        .when(pl.col("param").eq("loc")).then(x[0])
        .when(pl.col("param").eq("scale")).then(pl.col("actual").mul(0.5))
        .when(pl.col("param").eq("skew")).then(-np.inf)
        .alias('lb')
    )  # fmt: skip

    return df


def _gen_random_parameters(
    df: pl.DataFrame,
    lb: float = 0.7,
    ub: float = 1.3,
    seed: float | int | str = constants.SEED,
):
    """
    Create a table in the form of the parameter table but with randomized values for each row as a multiple of a factor within the bounds
    """

    # establish a reproducible state through the seed
    random.seed(seed)

    # generate a list of random values the same length as the df
    random_values = [random.uniform(lb, ub) for x in range(len(df))]

    # add the factors to the df and mutate the values by multiplication by the factor
    factors = pl.Series(name="factor", values=random_values)
    df_ = df.with_columns(factors).select(
        pl.col("peak"),
        pl.col("param"),
        pl.col("actual").mul(pl.col("factor")).alias("randomized"),
    )

    return df_


def _gen_p0_tbl(param_tbl: SkewNormParams2Peaks) -> P0Tbl:
    """
    calculate p0 as a random variation from the input parameters that generated the test data
    """

    # name the 'randomized' column as 'p0' before returning
    p0 = _gen_random_parameters(df=param_tbl, lb=0.7, ub=1.3).rename(
        {"randomized": "p0"}
    )

    return p0
