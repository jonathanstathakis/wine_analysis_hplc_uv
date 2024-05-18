"""
Test the function of the `PipelineETL` class
"""

import duckdb as db
import pytest
from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import etl_pipeline
from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import generic

from wine_analysis_hplc_uv.etl.post_build_library.pbl_oop import (
    transformers as etl_tformers,
)

from tests.test_etl.test_post_build_library.test_build_library_oop.gen_sample_test_data import (
    GenSampleCSWide,
)

pytest.skip(allow_module_level=True, reason="test subjects have been depreceated..")


@pytest.mark.parametrize("write_to_db", [(False,), (True,)])
def test_etl_pipeline_1_transformer(
    con: db.DuckDBPyConnection,
    gen_sample_cs_wide: GenSampleCSWide,
    write_to_db: bool,
):
    """
    test whether the pipeline 'write_to_db' function occurs by testing whether the temporary table from CSWideToLong is present in the database during the session.
    """

    try:
        input_tblname = gen_sample_cs_wide.output_tblname
        output_tblname = "cs_sample_long"
        transformers = {
            "cs_wide_to_long": etl_tformers.CSWideToLong(
                output_tblname=output_tblname, input_tblname=input_tblname
            )
        }

        pipeline = etl_pipeline.PipelineETL(
            con=con, transformers=transformers, write_to_db=write_to_db
        )

        pipeline.execute_pipeline()

        if not write_to_db:
            assert generic.tbl_exists(con=con, tbl_name=output_tblname, tbl_type="temp")
        elif write_to_db:
            assert generic.tbl_exists(con=con, tbl_name=output_tblname, tbl_type="base")
        else:
            raise ValueError(f"expect bool for {write_to_db=}")
    except Exception as e:
        raise e
    finally:
        pipeline._invert_pipeline()


@pytest.mark.parametrize("write_to_db", [(False,), (True,)])
def test_etl_pipeline_multiple_transformers(
    write_to_db: bool,
    gen_sample_cs_wide: GenSampleCSWide,
    con: db.DuckDBPyConnection,
    cs_tbl_output: str = "cs_long_test",
    sm_tbl_output: str = "sample_metadata_test",
):
    """
    test whether the Pipeline can create the two tables from input.
    """
    cs_tbl_input = gen_sample_cs_wide.output_tblname

    transformers = {
        "cs_wide_to_long": etl_tformers.CSWideToLong(
            input_tblname=cs_tbl_input, output_tblname=cs_tbl_output
        ),
        "sample_metadata_join": etl_tformers.BuildSampleMetadata(
            output_tblname=sm_tbl_output
        ),
    }

    pipe = etl_pipeline.PipelineETL(
        con=con, transformers=transformers, write_to_db=write_to_db
    )

    try:
        pipe.execute_pipeline()

        assert generic.tbl_exists(con=con, tbl_name=cs_tbl_output)
        assert generic.tbl_exists(con=con, tbl_name=sm_tbl_output)
    except Exception as e:
        raise e
    finally:
        for tformer in pipe.transformers.values():
            tformer.cleanup()
