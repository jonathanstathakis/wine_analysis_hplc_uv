def plot_3d_line(uv_data, plot_title):
    
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