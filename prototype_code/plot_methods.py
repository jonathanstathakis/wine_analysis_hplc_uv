from plotly import graph_objects as go
import pandas as pd

def plot_signal_in_series(df : pd.DataFrame, series_key, x_key, y_key):
    fig = go.Figure()
    for idx, row in df.iterrows():
        fig.add_trace(go.Scatter(x = row[series_key][x_key], y = row[series_key][y_key], mode = 'lines',name = row.name, text = row.name))
    return fig

def plot_signal_from_df_in_dict(dict_of_df : dict, x_key, y_key):
    fig = go.Figure()

    print(dict_of_df)
    for key, chromatogram_df in dict_of_df.items():
        print(key)
        fig.add_trace(go.Scatter(x = chromatogram_df[x_key], y = chromatogram_df[y_key], mode = 'lines', name = key, text = key))
    fig.update_layout(
        legend = dict(
        x = 0.5,
        y = -0.1,
        xanchor = 'center',
        yanchor = 'top',
        orientation = 'h',
        traceorder = 'normal'),
        margin = dict(b=100)
    )
    return fig