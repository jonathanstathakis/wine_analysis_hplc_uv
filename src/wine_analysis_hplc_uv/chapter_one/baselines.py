"""
Baseline calculation functions
"""

import duckdb as db
from pybaselines import whittaker
from datetime import datetime
import polars as pl
from wine_analysis_hplc_uv.chapter_one import polars_extension


class TblCreator:
    def __init__(self):
        """
        class responsible for creating tables with homogenous metadata, stores the datetime
        at the time of instantiation, representing a transaction.
        """
        self.now = datetime.now()

    def create_table(self, x, colname: str) -> pl.DataFrame:
        """
        create a 1 column table from `x` with `colname`
        """

        return pl.DataFrame({colname: x})

    def add_metadata(self, df: pl.DataFrame, sample_num: str, dt: str) -> pl.DataFrame:
        """
        add metadata to input dataframe, use to homogenise metadata across created tables
        """
        df_ = df.with_columns(
            sample_num=pl.lit(sample_num), dt=pl.lit(dt)
        ).with_row_index("idx")
        return df_

    def build_output_table(self, x, value_name, sample_num: str) -> pl.DataFrame:
        """
        take an input `x` with label `value_name` and output a dataframe with required metadata
        """

        tbl = self.create_table(x=x, colname=value_name)
        tbl_ = self.add_metadata(df=tbl, sample_num=sample_num, dt=self.now)
        return tbl_


tbl_creator = TblCreator()


def calculate_baselines(
    df: pl.DataFrame, grp_col: str, y_col: str
) -> tuple[pl.DataFrame, dict[str, pl.DataFrame]]:
    """
    calculate the baseline using asls and return the results as an object of tables with the calculated parameters
    :param signals_together: if true,
    """
    baselines_list = []
    weights_list = []
    tol_history_list = []
    corrected_list = []

    for grp_key, df in df.partition_by(
        [grp_col], maintain_order=True, as_dict=True
    ).items():
        # get the sample_num
        sample_num = grp_key[0]

        # generate the fitted baseline and iteration parameters
        lam = 1e6
        p = 0.01
        diff_order = 2
        max_iter = 50
        tol = 0.001
        data = df[y_col]

        baseline_array, params_dict = whittaker.asls(
            lam=lam,
            p=p,
            diff_order=diff_order,
            max_iter=max_iter,
            tol=tol,
            data=data,
        )

        # correct the signal by the baseline

        corrected_array = data - baseline_array

        # extract the parameters as arrays
        weights_array, tol_history_array = (
            params_dict["weights"],
            params_dict["tol_history"],
        )

        baseline_tbl = tbl_creator.build_output_table(
            x=baseline_array, value_name="baseline", sample_num=sample_num
        )
        baselines_list.append(baseline_tbl)

        corrected_tbl = tbl_creator.build_output_table(
            x=corrected_array, value_name="corrected", sample_num=sample_num
        )
        corrected_list.append(corrected_tbl)

        weights_tbl = tbl_creator.build_output_table(
            x=weights_array, value_name="weights", sample_num=sample_num
        )
        weights_list.append(weights_tbl)
        tol_history_tbl = tbl_creator.build_output_table(
            x=tol_history_array, value_name="tol_history", sample_num=sample_num
        )
        tol_history_list.append(tol_history_tbl)

        baselines = pl.concat(baselines_list).pipe(
            polars_extension.to_enum, col=grp_col
        )
        corrected = pl.concat(corrected_list).pipe(
            polars_extension.to_enum, col=grp_col
        )
        weights = pl.concat(weights_list).pipe(polars_extension.to_enum, col=grp_col)
        tol_history = pl.concat(tol_history_list).pipe(
            polars_extension.to_enum, col=grp_col
        )

    return join_baseline_result_signals(
        signal=df, baseline=baselines, corrected_signal=corrected
    ), dict(
        baselines=baselines,
        weights=weights,
        tol_history=tol_history,
        corrected=corrected,
    )


def join_baseline_result_signals(
    signal: pl.DataFrame, baseline: pl.DataFrame, corrected_signal: pl.DataFrame
) -> pl.DataFrame:
    """
    combine baseline, corrected and original signal in one table
    """

    join_query = """--sql
    select
        l.sample_num,
        l.idx,
        l.absorbance,
        r.baseline,
        rr.corrected
    from
        (select sample_num, idx, absorbance from signal) as l
    join
        (select sample_num, idx, baseline from baseline) as r
    on
        l.sample_num = r.sample_num
    and
        l.idx = r.idx
    join
        (select sample_num, idx, corrected from corrected_signal) as rr
    on
        l.sample_num = rr.sample_num
    and
        l.idx = rr.idx
    """
    return db.sql(join_query).pl().pipe(polars_extension.to_enum, "sample_num")
