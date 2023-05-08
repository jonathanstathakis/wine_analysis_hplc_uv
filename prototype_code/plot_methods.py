from plotly import graph_objects as go
import signal_data_treatment_methods as dt
import pandas as pd

def plot_signal_in_series(series : pd.Series, x_key, y_key):
    """
    Take a series of dfs, where the dfs are organised as RangeIndex | mins | signal and return a plotly fig of each df overlaid.
    """
    fig = go.Figure()
    for idx in series.index:
        x = series[idx][x_key]
        y = series[idx][y_key]
    
        # signals
        fig.add_trace(go.Scatter(x = x, y = y, mode = 'lines', name = idx, text = idx))

        # peaks
        peak_trace = get_trace_peak_maxima(series[idx])
        peak_trace['text'] = idx
        fig.add_trace(peak_trace)
        
    
    fig.update_layout(
        legend = dict(
        x = 0.5,
        y = -0.1,
        xanchor = 'center',
        yanchor = 'top',
        orientation = 'h',
        traceorder = 'normal'),
        margin = dict(b=100))
    
    return fig

def get_trace_peak_maxima(df : pd.DataFrame) -> go.Scatter:
    """
    Take a dataframe signal of shape RangeIndex | mins | signal and return a plotly trace of that dataframe signal's peaks. To be used within plot_signal_in_series as option.
    """
    x, y = df[df.columns[0]], df[df.columns[1]]
    
    peak_df = dt.peak_finder(x = x, y = y, in_height = 20, in_prominence=5)

    peak_x, peak_y = peak_df[peak_df.columns[0]], peak_df[peak_df.columns[1]]
    
    peak_trace = go.Scatter(x=peak_x, y=peak_y, mode='markers', showlegend=False, name = 'peak maxima', marker_symbol = 'x')

    return peak_trace
    
