import pandas as pd
import plotly.graph_objs as go
from scipy.signal import find_peaks


def color_scale():
    scale = [0.0, 0.002, 0.004, 0.006, 0.04, 0.2, 0.4, 0.5, 0.7, 1.0]

    import_colors = [
        "rgb(247,252,253)",
        "rgb(229,245,249)",
        "rgb(204,236,230)",
        "rgb(153,216,201)",
        "rgb(102,194,164)",
        "rgb(65,174,118)",
        "rgb(35,139,69)",
        "rgb(0,109,44)",
        "rgb(0,68,27)",
    ]

    colors = ["rgb(255, 255, 255)"]

    colors = colors + import_colors

    color_scale = [[scale[i], colors[i]] for i in range(len(scale))]

    return color_scale


def plot_3d_line(df, plot_title=None):
    """
    Takes a wide format uv data df with mins as column 1 and a default index, melts it into a long format then plots a 3d line plot.
    """
    try:
        melt_df = df.melt(id_vars="mins")
        melt_df.columns = ["mins", "nm", "mAU"]
        melt_df["nm"] = pd.to_numeric(melt_df["nm"])

    except Exception as e:
        print(e)

    color_scale = "Magma"

    x = melt_df["nm"]
    y = melt_df["mins"]
    z = melt_df["mAU"]


def plot_3d_line(df, plot_title=None):
    """
    Takes a wide format uv data df with mins as column 1 and a default index, melts it into a long format then plots a 3d line plot.
    """
    try:
        melt_df = df.melt(id_vars="mins")
        melt_df.columns = ["mins", "nm", "mAU"]
        melt_df["nm"] = pd.to_numeric(melt_df["nm"])

    except Exception as e:
        print(e)

    # Custom colorscale
    # Custom Magma-like colorscale

    # Group the data by the 'nm' column
    grouped = melt_df.groupby("nm")

    traces = []
    for _, group in grouped:
        x = group["nm"]
        y = group["mins"]
        z = group["mAU"]

        trace = go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            line=dict(
                color=z,
                colorscale=color_scale(),
                width=6,
                cmin=melt_df["mAU"].min(),
                cmax=melt_df["mAU"].max(),
            ),
            showlegend=False,
        )
        traces.append(trace)

    layout = go.Layout(width=800, height=800)

    fig = go.Figure(data=traces, layout=layout)

    return fig


def peak_plot(data=pd.DataFrame, nm=int, plot_title=str):
    peak_idx, peak_heights = find_peaks(data[nm], height=50, distance=50)

    cx = data[nm].index.values
    cy = data[nm].values
    px = data.index.values[peak_idx]
    py = data[nm].values[peak_idx]

    fig = go.Figure()

    fig.update_layout(title=f"{plot_title}, {nm}")

    peak_trace = go.Scatter(x=px, y=py, mode="markers", name="peaks")

    chrom_trace = go.Scatter(x=cx, y=cy, mode="lines", name="chromatogram")

    fig.add_trace(chrom_trace)

    fig.add_trace(peak_trace)

    fig.show()


def downsample(data, factor):
    return data[::factor]


def surface_plot(df, plot_title=None, downsample_factor=10):
    """
    Takes a wide format uv data df with mins as column 1 and a default index, melts it into a long format then plots a 3d surface plot.
    """

    # Pivot the data into a 2D matrix format
    z = df.drop(["mins"], axis=1)

    # Downsample the data
    z_downsampled = z.apply(lambda x: downsample(x, downsample_factor), axis=1)
    z_downsampled = downsample(z_downsampled, downsample_factor)

    # Create the x and y arrays corresponding to the columns and index of the pivot table
    x = z_downsampled.columns
    y = df["mins"]

    # Create the surface plot
    trace = go.Surface(x=x, y=y, z=z_downsampled, colorscale="Magma", showscale=False)

    layout = go.Layout(
        width=800,
        height=800,
        scene=dict(xaxis_title="nm", yaxis_title="mins", zaxis_title="mAU"),
    )

    fig = go.Figure(data=[trace], layout=layout)

    return fig


import pandas as pd


def downsample(data, factor):
    return data[::factor]


def contour_plot(df, plot_title=None, downsample_factor=10):
    """
    Takes a wide format uv data df with mins as column 1 and a default index, melts it into a long format then plots a contour plot.
    """
    # Pivot the data into a 2D matrix format
    z = df.drop(["mins"], axis=1)

    # Downsample the data
    z_downsampled = z.apply(lambda x: downsample(x, downsample_factor), axis=1)
    z_downsampled = downsample(z_downsampled, downsample_factor)

    # Create the x and y arrays corresponding to the columns and index of the pivot table
    x = z_downsampled.columns
    y = df["mins"]

    # Create the contour plot
    trace = go.Contour(
        x=x, y=y, z=z_downsampled, colorscale=color_scale(), showscale=False
    )

    layout = go.Layout(
        width=800, height=800, xaxis=dict(title="nm"), yaxis=dict(title="mins")
    )

    fig = go.Figure(data=[trace], layout=layout)

    return fig
