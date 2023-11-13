import pandas as pd
import numpy as np
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import datasets
from wine_analysis_hplc_uv import definitions


def run_models():
    # declare parameters

    md = datasets.MyData(definitions.DB_PATH)
    md.get_dset()

    append = True

    md.process_frame(
        md.raw_data_,
        resample_kwgs=dict(
            grouper=["id", "code_wine"],
            time_col="mins",
            original_freqstr="0.4S",
            resample_freqstr="2S",
        ),
        melt_kwgs=dict(
            id_vars=["detection", "color", "varietal", "id", "code_wine", "mins"],
            value_name="signal",
            var_name="wavelength",
        ),
        smooth_kwgs=dict(
            smooth_kwgs=dict(
                grouper=["id", "wavelength"],
                col="signal",
            ),
            append=append,
        ),
        bline_sub_kwgs=dict(
            prepro_bline_sub_kwgs=dict(
                grouper=["id", "wavelength"],
                col="smoothed",
                asls_kws=dict(max_iter=100, tol=1e-3, lam=1e5),
            ),
            append=append,
        ),
        pivot_kwgs=dict(
            columns=["detection", "color", "varietal", "id", "code_wine"],
            index="mins",
            values="bcorr",
        ),
    )

    print(md.processed_data_)


def main():
    run_models()


if __name__ == "__main__":
    main()
