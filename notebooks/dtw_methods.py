import pandas as pd
import seaborn as sns


class DTWNotebookMethods:
    """
    A class containing methods for [dynamic_time_warping](./dynamic_time_warping.ipynb)
    """

    def query_ref_align_plot(x, y, x_align):
        # plot 3 side-by-side subplots first of the query and ref, then the warped query and ref
        # and finally the query and warped query
        data = (
            x.join(y)
            .join(x_align)
            .sort_index(axis=1)
            .pipe(
                lambda df: df.set_axis(
                    axis=1,
                    labels=df.columns.set_names(
                        ["sample", "status", "window_size", "unit"]
                    ),
                )
            )
        )

        sp1 = data.loc[:, pd.IndexSlice[:, ["query", "ref"]]].pipe(
            lambda df: df.set_axis(
                axis=1,
                labels=pd.MultiIndex.from_frame(
                    df.columns.to_frame().assign(subplot="query and reference")
                ),
            )
        )

        # sp2 is aligned and ref

        sp2 = data.loc[:, pd.IndexSlice[:, ["aligned", "ref"]]].pipe(
            lambda df: df.set_axis(
                axis=1,
                labels=pd.MultiIndex.from_frame(
                    df.columns.to_frame().assign(subplot="aligned query and reference")
                ),
            )
        )

        ## sp3 is query and aligned

        sp3 = data.loc[:, pd.IndexSlice[:, ["query", "aligned"]]].pipe(
            lambda df: df.set_axis(
                axis=1,
                labels=pd.MultiIndex.from_frame(
                    df.columns.to_frame().assign(subplot="query and aligned query")
                ),
            )
        )

        # concatenate the three subplot dataframes, melt, renaming the value column to 'mAU', convert the date time index to a minutes float, create a column-wise facetgrid on 'subplot', map a lineplot to the facetgrids of 'mins', 'mAU', 'status' for hue, set the subplot titles to subplot value.

        plotdata = pd.concat([sp1, sp2, sp3], axis=1)

        g = (
            plotdata.melt(ignore_index=False, value_name="mAU")
            .pipe(lambda df: df.set_index(df.index.total_seconds() / 60))
            .pipe(
                lambda df: sns.FacetGrid(df, col="subplot", aspect=2, height=5)
                .map_dataframe(sns.lineplot, x="mins", y="mAU", hue="status")
                .set_titles(col_template="{col_name}")
            )
        )

        return (plotdata, g)
