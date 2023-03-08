def plot_3d_line(uv_data, plot_title = None):
    
    """
    Takes a wide format uv data df with mins as column 1 and a default index, melts it into a long format then plots a 3d line plot.
    """
    
    # Set up the environment

    import rainbow as rb

    from pathlib import Path

    import pandas as pd

    from plotly import __version__ 

    from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

    from plotly import express as px

    melt_uv_df = uv_data.melt(id_vars = "mins")
    
    try:

        melt_uv_df.columns = ['mins', 'nm', 'mAU']

        melt_uv_df['nm'] = pd.to_numeric(melt_uv_df['nm'])
    
    except Exception as e:
        print(e)

    fig = px.line_3d(melt_uv_df,
                     x = 'nm',
                     y = 'mins',
                     z = 'mAU',
                     color = 'nm',
                     title = plot_title,
                     template = 'plotly_dark'
                    )

    fig.update_layout(width = 800, height = 800)
    
    fig.update_traces(line=dict(width=4))

    display(fig)
    
import pandas as pd

from pathlib import Path
    
import plotly.graph_objs as go

from scipy.signal import find_peaks

def peak_plot(data = pd.DataFrame, nm = int, plot_title = str):

    peak_idx, peak_heights = find_peaks(data[nm], height = 50, distance = 50)

    cx = data[nm].index.values

    cy = data[nm].values

    px = data.index.values[peak_idx]

    py = data[nm].values[peak_idx] 

    fig = go.Figure()

    fig.update_layout(title = f"{plot_title}, {nm}")

    peak_trace = go.Scatter(x = px, y = py, mode = 'markers', name = 'peaks')

    chrom_trace = go.Scatter(x = cx, y = cy, mode = 'lines', name = 'chromatogram')

    fig.add_trace(chrom_trace)

    fig.add_trace(peak_trace)

    fig.show()