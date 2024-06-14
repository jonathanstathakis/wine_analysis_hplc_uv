"""
A plot of ...
"""

from wine_analysis_hplc_uv.chapter_one import get_raw_shiraz
import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl

pl.Config.set_tbl_cols(20)


def get_figure_one():
    shiraz = get_raw_shiraz.get_raw_shiraz()
    print(shiraz)
    sns.lineplot(
        data=shiraz.cast({"sample_num": pl.String}),
        x="mins",
        y="absorbance",
        hue="sample_num",
    )
    plt.show()


get_figure_one()
