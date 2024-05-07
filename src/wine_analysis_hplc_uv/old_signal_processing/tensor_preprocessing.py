"""
2023-08-08 00:41:26

Part 1 of the preprocesing pipeline, forming the data structures. Initially going with a wide multiindex dataframe. Will probably have to go with individual variable dataframes for each matrix, so to speak, rather than an array-like structure.

1. [x] identify sample set.
2. [x] get sample set into a list-like.
3. [x] form a multinddexed dataframe.

The spectrum-chromatograms are obtainable via the pca module methods. They will be arriving in long form. We can simply pivot onto a multiindex of (wine, wavelength) to form the expected shape.

See [Establishing a Preprocessing Pipeline](/Users/jonathan/mres_thesis/notes/mres_logbook.md#Establishing-a-Preprocessing-Pipeline) for more information

2023-08-10 11:33:04

Parts of the pipe to add

1. [ ] time axis interpolation (need to clarify why this is necessary)
2. [ ] resampling (clarify what this is)
3. [ ] savitzky-golay filtering to smooth and denoise.
4. [ ] baseline correction through a PLS derivative.
5. [ ] intensity normalization on maxima in dataset.
6. [ ] alignment
"""

from wine_analysis_hplc_uv.db_methods import get_data
from wine_analysis_hplc_uv.modeling import pca
from wine_analysis_hplc_uv import definitions
import duckdb as db


def get_frames(con):
    get_data.get_wine_data(
        con, samplecode=("124", "130", "125", "133", "174"), wavelength=(450,)
    )
    df = con.sql("select * from wine_data").df().pipe(pca.pivot_wine_data)

    return df


def main():
    con = db.connect(definitions.DB_PATH)
    df = get_frames(con)


if __name__ == "__main__":
    main()
