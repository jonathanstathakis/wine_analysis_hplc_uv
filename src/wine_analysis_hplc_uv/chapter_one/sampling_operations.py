"""
contain functions relevant to producing samples from datasets
"""

import polars as pl
import duckdb as db
from wine_analysis_hplc_uv.chapter_one import polars_extension


def sample_table_by_groups(
    df: pl.DataFrame, sampling_col: str, num_samples: int
) -> pl.DataFrame:
    """
    take `num_samples` of groups labeled by `sampling_col` in `df`.
    """
    sampling_query = f"""--sql
    select
        *
    from
        df
    where
        {sampling_col} in (
        select
            {sampling_col}
        from
            (select
                distinct {sampling_col}
            from
                df)
        using sample reservoir ({num_samples} rows) repeatable (1000))
    """

    sampled = db.sql(sampling_query).pl()

    # test result by checking that the number of distinct values in the sampling col
    # matches `num_samples`

    test_query = f"""--sql
    select
        count (distinct {sampling_col}) = {num_samples} as num_distinct_eq_input
    from
        sampled
    """
    assert (
        db.sql(test_query).pl().item()
    ), "after sampling, distinct groups != user input"

    return sampled.pipe(polars_extension.to_enum, "sample_num")
