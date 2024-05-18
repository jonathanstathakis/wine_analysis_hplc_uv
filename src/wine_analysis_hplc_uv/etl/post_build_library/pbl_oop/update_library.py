"""
2024-05-04 01:18:03

contains the process necessary to get the database into what I am considering the base state for EDA. That is, a metadata table that is filterable to select data subsets, and an efficiently queryable spectrum_chromatogram table containg the spectrum_chromatogram images, where we define an image as a 2D signal. See [etl](notes/etl.md#process)
"""

from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import (
    etl_pipeline,
)
from wine_analysis_hplc_uv import definitions
import duckdb as db
import logging

from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import (
    transformers as etl_tformers,
)

logger = logging.getLogger(__name__)


def update_library(
    con: db.DuckDBPyConnection,
    overwrite: bool = True,
    write_to_db: bool = False,
    cs_input_tblname="chromatogram_spectra",
    cs_output_tblname="chromatogram_spectra_long",
    sm_output_tbname="sample_metadata",
) -> list[str]:
    """
    TODO: include args for the input sample_metadata tables
    """

    tformers = {
        "sample_metadata": etl_tformers.BuildSampleMetadata(
            output_tblname=sm_output_tbname
        ),
        "cs_wide_to_long": etl_tformers.CSWideToLong(
            input_tblname=cs_input_tblname, output_tblname=cs_output_tblname
        ),
    }
    pipeline = etl_pipeline.PipelineETL(
        con=con, transformers=tformers, overwrite=overwrite, write_to_db=write_to_db
    )

    new_tbls = []
    try:
        logger.info("Updating library..")
        new_tbls: list[str] = pipeline.execute_pipeline()
        logger.info("Library update complete..")
    except Exception as e:
        raise e

    return new_tbls


def main():
    con = db.connect(definitions.DB_PATH)
    update_library(con=con, overwrite=True, write_to_db=True)


if __name__ == "__main__":
    main()
