import sys

import os

# adds root dir 'wine_analyis_hplc_uv' to path.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from agilette import agilette_core as ag

import matplotlib.pyplot as plt

ag = ag.Agilette("/Users/jonathan/0_jono_data")

# plot_0002 = ag.data_file_dir.sequences['2023-03-01_15-22-02_ACETONE_VOID-VOL-MEASUREMENT.sequence'].data_files['acetone0002'].extract_ch_data()['279.0']['data'].plot(x = 'mins')

coffee_248 = ag.data_file_dir.single_runs[
    "2023-02-23_LOR-RISTRETTO.D"
].extract_ch_data()["248.0"]

coffee_248["data"].plot(
    x="mins", y="mAU", title=coffee_248["signal_info"], legend=False
)

plt.show()

# print(test_plot)
