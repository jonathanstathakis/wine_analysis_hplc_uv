"""
data specific to "characterising and normalizing time axis"
"""

import duckdb as db
from wine_analysis_hplc_uv import definitions


def fetch_154():
    """
    retrieve the 154 sample from the database, at 450nm
    """
    con = db.connect(definitions.DB_PATH)

    query = """--sql
            SELECT
                wine, mins, absorbance
            FROM
                chromatogram_spectra_long cs 
            LEFT JOIN
                sample_metadata sm
            USING
                (id)
            WHERE
                samplecode='154'
            AND 
                wavelength=450
            ORDER BY
                mins ASC
            """
    return con.sql(query).pl()


df_154 = fetch_154()
