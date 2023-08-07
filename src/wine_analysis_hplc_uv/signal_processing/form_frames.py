"""
2023-08-08 00:41:26

Part 1 of the preprocesing pipeline, forming the data structures. Initially going with a wide multiindex dataframe. Will probably have to go with individual variable dataframes for each matrix, so to speak, rather than an array-like structure.

1. [ ] identify sample set.
2. get sample set into a list-like.
3. form a multinddexed dataframe.

The spectrum-chromatograms are obtainable via the pca module methods. They will be arriving in long form. We can simply pivot onto a multiindex of (wine, wavelength) to form the expected shape.

See [Establishing a Preprocessing Pipeline](/Users/jonathan/mres_thesis/notes/mres_logbook.md#Establishing-a-Preprocessing-Pipeline) for more information
"""


def get_frames():
    return None
