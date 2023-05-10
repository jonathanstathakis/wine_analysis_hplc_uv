from plotly import graph_objects as go
import signal_data_treatment_methods as dt
import pandas as pd
import plotly.io as pio
import numpy as np

def plot_signal_in_series(series : pd.Series, x_key, y_key):
    """
    Take a series of dfs, where the dfs are organised as RangeIndex | mins | signal and return a plotly fig of each df overlaid.
    """
    fig = go.Figure()

    for sample_name in series.index:

        data_df = series[sample_name]
        x = data_df[x_key]
        y = data_df[y_key]
    

        # peaks
        peak_df = get_peak_df(data_df)
        #peak_df['text'] = id
        
        # signals
        fig.add_trace(go.Scatter(x = x, 
                                 y = y, 
                                 mode = 'lines',
                                 name = sample_name,
                                 text = sample_name,
                                 opacity = 0.65))

        peak_maxima_marker_ratio = 0.03
        peak_maxima_marker_fill_color = 'red'

        # add peak maxima trace
        for idx, row in peak_df.reset_index(drop = True).iterrows():
            xi, yi = row['peak_x'], row['peak_y']
            peak_idx = idx + 1

            customdata = np.array([[xi, yi]])

            name = f'{sample_name} peak #{peak_idx}'
            
            fig.add_trace(go.Scatter(x = [xi],
                                    y = [yi],
                                    marker_symbol = 'circle',
                                    mode = 'markers',
                                    opacity = 0.0,
                                    showlegend = False,
                                    name = name,
                                    hovertemplate=f'{name}:<br>{xi:.3f}, {yi:.3f}<extra></extra>'
                                    ))
            
            x_range = x.max() - x.min()
            y_range = y.max() - y.min()
            

            shape_size_x = x_range * peak_maxima_marker_ratio/4
            shape_size_y = y_range * peak_maxima_marker_ratio*2

            # forward slash
            fig.add_shape(
                        type = 'line',
                          yref = 'y',
                          x0 = xi - shape_size_x/2,
                          x1 = xi + shape_size_x/2,
                          y0 = yi - shape_size_y/2,
                          y1 = yi + shape_size_y/2,
                          line=dict(color=peak_maxima_marker_fill_color, width = 2),
                          fillcolor = peak_maxima_marker_fill_color,
                          opacity = 0.75
                          )
            
            # back slash
            fig.add_shape(
                        type = 'line',
                          yref = 'y',
                          x0 = xi + shape_size_x/2,
                          y0 = yi - shape_size_y/2,
                          x1 = xi - shape_size_x/2,
                          y1 = yi + shape_size_y/2,
                          line=dict(color=peak_maxima_marker_fill_color, width = 2),
                          fillcolor = peak_maxima_marker_fill_color,
                          opacity = 0.75
                          )
            
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

def get_peak_df(df : pd.DataFrame) -> go.Scatter:
    """
    Take a dataframe signal of shape RangeIndex | mins | signal and return a plotly trace of that dataframe signal's peaks. To be used within plot_signal_in_series as option.
    """
    x, y = df[df.columns[0]], df[df.columns[1]]
    x_range = x.max() - x.min()
    y_range = y.max() - y.min()

    min_height = y_range / len(y)

    peak_df = dt.peak_finder(x = x, y = y, in_height = min_height, in_prominence=0.1)

    peak_x, peak_y = peak_df[peak_df.columns[0]], peak_df[peak_df.columns[1]]

    peak_marker_trace = go.Scatter(x = peak_x, y = peak_y, marker_symbol = 1)

    # make this oen invisible
    #peak_trace = go.Scatter(x=peak_x, y=peak_y, mode='markers', showlegend=False, name = 'peak maxima', marker_symbol = 'x')

    return peak_df
    
