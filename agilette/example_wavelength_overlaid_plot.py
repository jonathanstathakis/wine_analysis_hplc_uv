"""
An example of how to plot an overlay of wavelength signals for a single run.
"""
import sys

import os

# adds root dir 'wine_analyis_hplc_uv' to path.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from agilette import agilette_core as ag

import plotly.graph_objs as go

fig = go.Figure()

print(os.listdir())

try:
    
    lor_ristretto = ag.Agilette('../example_data/').library.single_runs['2023-02-23_LOR-RISTRETTO.D']

    lor_ristretto_data = lor_ristretto.extract_ch_data()

    def coffee_wavelength_plots(wavelength_data):

        coffee_248_plot = go.Scatter(x = wavelength_data.data_df['mins'], y = wavelength_data.data_df['mAU'], mode = 'lines', name = f'{wavelength_data.wavelength}')

        fig.add_trace(coffee_248_plot)

    for key in lor_ristretto_data.keys():
        coffee_wavelength_plots(lor_ristretto_data[key])

    fig.update_layout(title = f"{lor_ristretto.path.name}")

    fig.show()

except Exception as e:
    print(e)