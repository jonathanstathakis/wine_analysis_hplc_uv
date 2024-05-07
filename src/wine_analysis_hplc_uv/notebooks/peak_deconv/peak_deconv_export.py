"""
2023-11-20 10:09:45

This module will contain a method to export the output of peak deconvolution to a DB
table. Specifically, it will handle chunkwise insertion, as this process will both be
slow and iterative as we develop better deconvolution methods.

2023-11-20 10:26:30

Whats the schema? ID + the fields from the peak table.
"""

from wine_analysis_hplc_uv import definitions

from wine_analysis_hplc_uv.notebooks.peak_deconv import db_interface


def main():
    dbpath = definitions.DB_PATH
    dbint = db_interface.DBInterface(dbpath)

    tblname = "test"

    dbint.drop_tbl(tblname=tblname)

    df = dbint.load_dataset("penguins")

    # tblname = 'chromatogram_spectra'

    dbint.insert_df_into_table(df, tblname=tblname)

    dbint.describe_table(tblname=tblname)


if __name__ == "__main__":
    main()
