"""
module containing functions returning samples from the database
"""

import duckdb as db
from wine_analysis_hplc_uv.chapter_one import polars_extension


def get_samples(
    con: db.DuckDBPyConnection,
    detection: str,
    n_samples: int,
    distinct_wine: bool = True,
):
    """
    :param distinct: if True, use `DISTINCT` keyword to only select one sample per 'wine'. This is a random selection, if specific representatives of a wine are required, do not use this function.

    select random samples with distinct wines - the selection from duplicate wine representatives is psuedorandom

    see <https://duckdb.org/docs/sql/samples.html> for information about sampling
    """
    if distinct_wine:
        distinct_str = "distinct"
    else:
        distinct_str = ""
    sampling_query = f"""--sql
    with sample_metadata as (
    select
        {distinct_str} wine,
        detection,
        acq_date,
        color,
        varietal,
        sample_num,
        id,
    from
        pbl.sample_metadata
    where
        detection='{detection}'
    ),
    random_samples as (
        select
            *
        from
            sample_metadata
        using sample
            ({n_samples} rows)
        repeatable
            (42)
        ),
    samples as (
    select
        sm.sample_num,
        sm.acq_date,
        sm.detection,
        sm.wine,
        sm.color,
        sm.varietal,
        sm.id,
        cs.idx,
        cs.mins,
        cs.absorbance,
    from
        pbl.chromatogram_spectra_long as cs
    join
        random_samples as sm
    on
        cs.id=sm.id
    where
        cs.wavelength=256
    order by
        sm.sample_num, cs.idx
    )
    select * from samples
    """
    sampling = con.sql(sampling_query).pl()

    sampling = polars_extension.to_enum(sampling, "sample_num")
    return sampling
