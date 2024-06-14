"""
Contains functions for obtaining datasets
"""

import duckdb as db
import polars as pl


def get_raw_shiraz(con: db.DuckDBPyConnection) -> pl.DataFrame:
    """
    extract the raw detected shiraz at 256 nm.
    """
    query = """
    select
        sm.wine as wine,
        sm.detection,
        sm.samplecode,
        sm.sample_num,
        cs.idx,
        cs.mins,
        cs.absorbance
    from
        pbl.chromatogram_spectra_long as cs
    left join
        pbl.sample_metadata as sm
    on
        sm.id=cs.id
    where
        wavelength=256
    and
        varietal='shiraz'
    and
        detection='raw'
    and
        mins<30
    order by
        sm.sample_num, cs.idx
    """

    shiraz = con.sql(query)

    return shiraz.pl()
