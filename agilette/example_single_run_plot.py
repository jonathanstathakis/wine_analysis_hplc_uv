"""
An example of how to plot a single wavelength from a single run.
"""
import sys

import os

# adds root dir 'wine_analyis_hplc_uv' to path.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from agilette import agilette_core as ag

import plotly.graph_objs as go

fig = go.Figure()

coffee_248 = ag.Agilette('../example_data/').library.single_runs['2023-02-23_LOR-RISTRETTO.D'].extract_ch_data()['248.0']

coffee_248_plot = go.Scatter(x = coffee_248.data_df['mins'], y = coffee_248.data_df['mAU'], mode = 'lines', name = f'{coffee_248.path.parent}, {coffee_248.wavelength}nm')

fig.add_trace(coffee_248_plot)

fig.update_layout(title = f"{coffee_248.path.parent.name}, {coffee_248.wavelength}nm", xaxis_title = coffee_248.data_df.columns[0], yaxis_title = coffee_248.data_df.columns[1])

fig.show()