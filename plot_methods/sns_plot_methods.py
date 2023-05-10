import seaborn as sns
from scripts.core_scripts import signal_data_treatment_methods as dt
import pandas as pd
import matplotlib.pyplot as plt

def plot_signal_in_series(series : pd.Series, x_key, y_key):
    """
    Take a series of dfs, where the dfs are organised as RangeIndex | mins | signal and return a plotly fig of each df overlaid.
    """
    fig, ax = plt.subplots()

    for idx in series.index:
    
        # signals
        sns.lineplot(data = series[idx], x = x_key, y = y_key, ax = ax, alpha = 0.5)

        # peaks
        peak_df = get_trace_peak_maxima(series[idx])

        sns.scatterplot(peak_df, x = 'peak_x', y = 'peak_y', ax = ax)

        # fig.update_layout(
    #     legend = dict(
    #     x = 0.5,
    #     y = -0.1,
    #     xanchor = 'center',
    #     yanchor = 'top',
    #     orientation = 'h',
    #     traceorder = 'normal'),
    #     margin = dict(b=100))
    
    return fig

def get_trace_peak_maxima(df : pd.DataFrame):
    """
    Take a dataframe signal of shape RangeIndex | mins | signal and return a plotly trace of that dataframe signal's peaks. To be used within plot_signal_in_series as option.
    """
    x, y = df[df.columns[0]], df[df.columns[1]]
    
    peak_df = dt.peak_finder(x = x, y = y, in_height = 20, in_prominence=5)

    peak_df[peak_df.columns[0]], peak_df[peak_df.columns[1]]

    return peak_df
    
