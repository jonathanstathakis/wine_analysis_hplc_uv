from wine_analysis_hplc_uv.old_signal_processing.sigpro_methods.standardize_time import (
    _resample,
)
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt


def test_resample(
    test_data_l: pl.DataFrame,
    time_col: str = "mins",
    value_col: str = "value",
    group_col: str = "samplecode",
    label_cols: list[str] = ["samplecode", "wine"],
) -> None:
    """
    test resampling routine
    """

    df_ = _resample.resample_to_mean_freq(
        df=test_data_l,
        time_col=time_col,
        value_col=value_col,
        group_col=group_col,
        label_cols=label_cols,
    )

    # plot_results(df=df_, x_col=time_col, y_col=value_col, grp_col=group_col)

    # to test, get the mean freq of `test_data_l`, and compare it to the freq of each group in df_. Each group should have the same frequency as the mean after transformation

    # compute the mean dx over the samples before transformation
    mean_dx = (
        test_data_l.select(pl.col("mins").diff().mean().over("samplecode"))
        .mean()
        .item()
    )

    # calculate the mean dx by sample after transformation
    check_aggs = df_.groupby("samplecode").agg(
        pl.col("mins").diff().mean().alias("mean_dx_tform")
    )

    # assert that all the mean dx are equal to the `mean_freq`. Have to round to 5 sig fig because polars is rounding the `mean_freq` for some reason

    is_all_eq = (
        check_aggs.with_columns(pl.lit(mean_dx).alias("mean_dx"))
        .select(pl.col("mean_dx_tform").round(5).eq(pl.col("mean_dx").round(5)).all())
        .item()
    )

    assert is_all_eq, "samplewise mean dx not equal to dataset mean dx!"


def plot_results(df: pl.DataFrame, x_col: str, y_col: str, grp_col: str) -> None:
    """
    plot the results as a line plot grid
    """

    sns.relplot(data=df, x=x_col, y=y_col, col=grp_col, col_wrap=2, kind="line")
    plt.show()
