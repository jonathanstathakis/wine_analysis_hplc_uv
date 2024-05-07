# ETL

Notes on the ETL of the database go here.

## Process

TODO: describe the full process to load the 'default state' of the database.

2024-05-04 01:21:37

ATM the module [ide](../src/wine_analysis_hplc_uv/ide.py) contains the methods required to go from the 'old' default state, to the new one. That is, one where there is a metadata table containing information about every single sample, ready for filtering, and a long from chromatogram_spectra table ready for efficient joining. Wrapping the two behind a Python API with basic filtering parameters will enable users (me) to easily retrieve samples and their data based on given criteria.

To get there, after running the base ETL (to be expanded on, atm I cant remember the method to create it. "build_library"?) We need to run 'build_sample_metadata' and 'cs_wide_to_long'. TODO: combine these into a top level function "update_library", or something.

## Amendments to the Final Loading State

2024-05-02 14:58:36

A previous development decision ended the loading phase with a square (wide) chromatogram_spectra table with a column for each wavelength. This was an erroneous decision because it made querying difficult and required Python string logic in order to correctly filter wavelengths, amongst other problems.

This error has been rectified by the addition of `extract_data_new.cs_wide_to_long` (TODO: update the import path and module name when it is changed). It needs to be run after the square table is produced, and will write a long form table to the database.

Long term, we will need to supercede the wide table process by the long table, and then remove it completely.

TODO: replace the wide form process with long form
TODO: test and verify the ETL process