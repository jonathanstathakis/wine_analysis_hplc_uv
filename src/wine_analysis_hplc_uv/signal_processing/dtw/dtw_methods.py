import pandas as pd
import seaborn as sns
from dtwalign import dtw
from pybaselines import Baseline
from wine_analysis_hplc_uv.old_signal_processing.mindex_signal_processing import (
    SignalProcessor,
)

scipro = SignalProcessor()

idx = pd.IndexSlice


class DTWNotebookMethods:
    """
    A class containing methods for [dynamic_time_warping](./dynamic_time_warping.ipynb)
    """

    def dtw_align_series(self, x, y, kwargs=dict()):
        """
        align an input x to y passing kwargs to `dtw()`, returning a long form 4 level
        column indexed df of ('samplecode','status','window_size','unit').

        'status' refers to the state of the series, either query, aligned_query, or
        ref
        """
        x_align = (
            x.iloc[dtw(x=x, y=y, **kwargs).get_warping_path()]
            .pipe(
                lambda df: df.set_index(
                    pd.timedelta_range(start=df.index[0], end=df.index[-1], freq="2S")
                ).rename_axis("mins")
            )
            .pipe(
                lambda df: df.set_axis(
                    pd.MultiIndex.from_arrays(
                        [["176"], ["aligned"], [10], ["mAU"]],
                        names=["sample", "status", "window_size", "unit"],
                    ),
                    axis=1,
                )
            )
        )
        return x_align

    def query_ref_align_plot(self, x, y, x_align):
        # plot 3 side-by-side subplots first of the query and ref, then the warped query and ref
        # and finally the query and warped query

        data = x.join([y, x_align]).sort_index(axis=1)

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
                lambda df: sns.FacetGrid(df, col="subplot")
                .map_dataframe(sns.lineplot, x="mins", y="mAU", hue="status")
                .set_titles(col_template="{col_name}")
            )
        )

        return (plotdata, g)


class AlignPipe:
    """
    DTW based alignment pipeline. Summary of pipeline developed in [dynamic_time_warping]()./notebooks/dynamic_time_warping.ipynb)

    Requires a tidy dataframe as input (TODO: expand on this, add input validation)
    """

    def __init__(self):
        self.ref = None

    def align_pipe(self, df: pd.DataFrame, display: bool = True) -> pd.DataFrame:
        """
        Wrap all of the contained functions to produce a baseline corrected DTW aligned
        dataset
        """
        df = self.baseline_correct(df, display)
        df = self.align_set(df)
        df = self.combine_signal_role_levels(df)

        return df

    def baseline_correct(self, df: pd.DataFrame, display: bool = True):
        """
        Baseline correct samples in df.

        Expects a pd.TimedeltaIndex index.
        """
        df = df.copy()

        df = (
            df.melt(ignore_index=False, value_name="raw")
            .groupby("samplecode", group_keys=False)
            .apply(
                lambda grp: grp.assign(
                    bline=Baseline(grp.index.total_seconds()).asls(grp.raw, lam=1000)[0]
                )
            )
            .assign(bcorr=lambda df: df.raw - df.bline)
            .pivot(columns=["samplecode", "wine"], values=["raw", "bline", "bcorr"])
            .pipe(
                lambda df: df.set_axis(
                    df.columns.set_names(level=0, names="signal"), axis=1
                )
            )
            .reorder_levels(axis=1, order=["samplecode", "wine", "signal"])
            .sort_index(axis=1)
        )

        if display:
            self.viz_baseline_corr(df)
        return df

    def viz_baseline_corr(self, df: pd.DataFrame):
        """
        Display a relplot overlay original signal, baseline and corrected signal for each sample
        """
        (
            df.melt(ignore_index=False, value_name="mAU")
            # convert timedelta to float for human-readable plotting with seaborn
            .pipe(
                lambda df: (
                    df
                    if isinstance(df.index, float)
                    else df.set_axis(df.index.total_seconds() / 60)
                )
            )
            .assign(wine=lambda df: df.samplecode + ": " + df.wine)
            .pipe(
                sns.relplot,
                col="wine",
                col_wrap=2,
                hue="signal",
                x="mins",
                y="mAU",
                kind="line",
            )
            .set_titles(col_template="{col_name}")
            .add_legend()
        )

    def choose_reference(self, df: pd.DataFrame):
        """
        id the reference sample
        """
        return scipro.most_correlated(df)

    # add '(ref)' suffix to the reference wine of the dataset

    def label_reference(self, df: pd.DataFrame):
        """
        add suffix '(ref)' to wine string of reference sample
        """
        oname = df[self.ref].columns.get_level_values("wine")[0]
        new_name = oname + " (ref)"

        return df.rename({oname: new_name}, axis=1)

    def align_set(self, df: pd.DataFrame):
        self.ref = self.choose_reference(df)

        df = self.label_reference(df)

        y = df.loc[:, idx[self.ref, :, "bcorr"]]

        # add aligned series to original df through concatenation. Need to subset the original
        # with the warping path, reindex to 2S timedelta range, rename signal level to 'aligned
        # then concatentate with original df

        df = (
            df.loc[:, idx[:, :, "bcorr"]]
            .pipe(
                lambda df: df.groupby(
                    ["samplecode", "wine"], group_keys=False, axis=1
                ).apply(
                    lambda grp: pd.concat(
                        [
                            grp,
                            grp.iloc[dtw(x=grp, y=y).get_warping_path(), :].pipe(
                                lambda df: df.set_index(
                                    pd.timedelta_range(
                                        start=df.index[0], end=df.index[-1], freq="2S"
                                    )
                                )
                                .rename_axis("mins")
                                .rename({"bcorr": "aligned"}, axis=1)
                            ),
                        ],
                        axis=1,
                    )
                )
            )
            .pipe(
                lambda df: df.reindex(
                    axis=1,
                    labels=pd.MultiIndex.from_frame(
                        df.columns.to_frame()
                        .assign(role="query")
                        .assign(
                            role=lambda df: df.loc[:, "role"].where(
                                ~(df.samplecode.isin(self.ref)), "ref"
                            )
                        )
                    ),
                )
            )
            .reorder_levels(axis=1, order=["samplecode", "wine", "role", "signal"])
            .sort_index(axis=1)
        )
        return df

    def combine_signal_role_levels(self, df):
        # add column index level 'state' as algamation of 'signal' and 'role'

        new_index_ = (
            df.columns.to_frame(index=False)
            .assign(
                state=lambda df: df.signal.where(~(df.signal == "aligned"), "aligned")
                .where(~(df.signal == "bcorr"), "query")
                .where(~(df.role == "ref"), "ref")
            )
            .drop(["role", "signal"], axis=1)
        )

        new_index = pd.MultiIndex.from_frame(new_index_)
        df = df.set_axis(new_index, axis=1)

        return df


class RelPlotDFBuilder:
    """
    class to produce a relplot of dtw alignment for input dataframe, formulated in [dynamic_time_warping](./notebooks/dynamic_time_warping.ipynb)
    """

    def __init__(self, df):
        """
        Handle the assignment and duplication process and logic to form a relplot df index
        in the following fashion:

        | sample  | row  | col  | role  |
        |---------|------|------|-------|
        | sample1 | row1 | col1 | query |
        | sample1 | row1 | col1 | ref   |
        | sample1 | row1 | col2 | align |
        | sample1 | row1 | col2 | ref   |
        | sample1 | row1 | col3 | query |
        | sample1 | row1 | col3 | align |

        do for each row then concat horizontally.

        Expects a tidy df of column index with levels (for example):

        |    | samplecode      | wine                                  | state   |
        |---:|:----------------|:--------------------------------------|:--------|
        |  0 | 154             | 2020 leeuwin estate shiraz art series | aligned |
        |  1 | 154             | 2020 leeuwin estate shiraz art series | query   |
        |  2 | 176             | 2021 john duval wines shiraz concilio | ref     |
        |  3 | 176             | 2021 john duval wines shiraz concilio | ref     |
        |  4 | 177             | 2021 torbreck shiraz the struie 1     | aligned |
        |  5 | 177             | 2021 torbreck shiraz the struie 1     | query   |
        |  6 | torbreck-struie | 2021 torbreck shiraz the struie 2     | aligned |
        |  7 | torbreck-struie | 2021 torbreck shiraz the struie 2     | query   |

        It is generalized enough to handle any names for the levels, and any values
        (as long as the pattern is consistant), however the 'samplecode' and 'state'
        levels must be in the same order, seperated by 1 level.
        """

        self.df = df

        # create a df out of the df multiindex, drop any duplicates.
        self.column_index_df = (
            df.columns.to_frame(index=False)
            .set_index(["samplecode", "wine", "state"])
            .loc[lambda df: ~df.index.duplicated(keep="first"), :]
        )

        # get the samplecodes as an iterable
        samples = self.column_index_df.index.get_level_values("samplecode").unique()

        # for each sample form a df of 'query' series and 'ref' series, then concat
        # them together
        col1 = pd.concat(
            [self.build_col(sample, "176", "query", "ref", 1) for sample in samples]
        ).assign(row=lambda df: df.groupby("wine").ngroup() + 1)

        # for each sample form a df of 'aligned', 'ref', then concat together
        col2 = pd.concat(
            [self.build_col(sample, "176", "aligned", "ref", 2) for sample in samples]
        ).assign(row=lambda df: df.groupby("wine").ngroup() + 1)

        # for each sample form a df of 'query', 'aligned' for the same sample, then concat
        col3 = pd.concat(
            [
                self.build_col3(sample, "176", "query", "aligned", 3)
                for sample in samples
            ]
        ).assign(row=lambda df: df.groupby("wine").ngroup() + 1)

        # combine all the col dfs
        self.index_df = pd.concat([col1, col2, col3])

        self.test_index_df()

        self.join_df = self.join_df_index_df()

        self.test_join_df()

        self.build_relplot()

    def build_col(self, samplecode_1, samplecode_2, state_val_1, state_val_2, colnum):
        """
        combine query and reference for overlaying in col1
        samplecode_1 is the base sample, samplecode_2 is the overlay, or comparison.
        state_val_1 and state_val_2 correspond to the respective samplecode.

        Used for column 1 and column 2.
        """

        if samplecode_1 == samplecode_2:
            sample = self.column_index_df.loc[idx[samplecode_2, :, state_val_2], :]

        else:
            # get sample row
            sample = self.column_index_df.loc[idx[samplecode_1, :, state_val_1], :]

        # get the reference row, reindex it so its 'wine' (row) is s1
        if samplecode_1 == samplecode_2:
            ref = self.column_index_df.loc[idx[samplecode_2, :, state_val_2], :]

        else:
            wine = sample.index.get_level_values("wine")
            ref = self.column_index_df.loc[idx[samplecode_2, :, state_val_2], :].pipe(
                lambda df: df.set_axis(
                    df.index.remove_unused_levels().set_levels(
                        level=["wine"], levels=[wine]
                    )
                )
            )

        # assign row and column identifier to reference and sample rows
        col1 = pd.concat([sample, ref]).assign(col=colnum)

        return col1

    def build_col3(self, samplecode, ref_samplecode, state_val_1, state_val_2, colnum):
        """
        combined query and aligned. Refer to build_col for parameter descriptions
        Cant use 'build_col' because the reference sample doesnt have the same state
        values as the other samples.

        Maybe we can modify how the reference sample is handled. Maybe seperate prior
        to initializing the concatenations in __init__
        """

        if samplecode == ref_samplecode:
            col3 = self.column_index_df.loc[[samplecode]].assign(col=3)

        else:
            col3 = self.column_index_df.loc[
                idx[samplecode, :, [state_val_1, state_val_2]], :
            ].assign(col=colnum)

        return col3

    def test_index_df(self):
        """
        test whether the output ready index_df matches the expected content and structure
        """
        # the expected output of RelPlotIndexBuilder.index_df. orient = 'tight' retains multiindex

        left = pd.DataFrame.from_dict(
            {
                "index": [
                    ("154", "2020 leeuwin estate shiraz art series", "query"),
                    ("176", "2020 leeuwin estate shiraz art series", "ref"),
                    ("176", "2021 john duval wines shiraz concilio (ref)", "ref"),
                    ("176", "2021 john duval wines shiraz concilio (ref)", "ref"),
                    ("177", "2021 torbreck shiraz the struie 1", "query"),
                    ("176", "2021 torbreck shiraz the struie 1", "ref"),
                    ("torbreck-struie", "2021 torbreck shiraz the struie 2", "query"),
                    ("176", "2021 torbreck shiraz the struie 2", "ref"),
                    ("154", "2020 leeuwin estate shiraz art series", "aligned"),
                    ("176", "2020 leeuwin estate shiraz art series", "ref"),
                    ("176", "2021 john duval wines shiraz concilio (ref)", "ref"),
                    ("176", "2021 john duval wines shiraz concilio (ref)", "ref"),
                    ("177", "2021 torbreck shiraz the struie 1", "aligned"),
                    ("176", "2021 torbreck shiraz the struie 1", "ref"),
                    ("torbreck-struie", "2021 torbreck shiraz the struie 2", "aligned"),
                    ("176", "2021 torbreck shiraz the struie 2", "ref"),
                    ("154", "2020 leeuwin estate shiraz art series", "query"),
                    ("154", "2020 leeuwin estate shiraz art series", "aligned"),
                    ("176", "2021 john duval wines shiraz concilio (ref)", "ref"),
                    ("177", "2021 torbreck shiraz the struie 1", "query"),
                    ("177", "2021 torbreck shiraz the struie 1", "aligned"),
                    ("torbreck-struie", "2021 torbreck shiraz the struie 2", "query"),
                    ("torbreck-struie", "2021 torbreck shiraz the struie 2", "aligned"),
                ],
                "columns": ["col", "row"],
                "data": [
                    [1, 1],
                    [1, 1],
                    [1, 2],
                    [1, 2],
                    [1, 3],
                    [1, 3],
                    [1, 4],
                    [1, 4],
                    [2, 1],
                    [2, 1],
                    [2, 2],
                    [2, 2],
                    [2, 3],
                    [2, 3],
                    [2, 4],
                    [2, 4],
                    [3, 1],
                    [3, 1],
                    [3, 2],
                    [3, 3],
                    [3, 3],
                    [3, 4],
                    [3, 4],
                ],
                "index_names": ["samplecode", "wine", "state"],
                "column_names": [None],
            },
            orient="tight",
        )

        pd.testing.assert_frame_equal(left=left, right=self.index_df)

    def join_df_index_df(self):
        """
        massage df and index_df to left join onto index_df
        """

        pdf = (
            self.df.melt(ignore_index=False, value_name="mAU")
            .reset_index()
            .set_index(["samplecode", "state"])
            .drop("wine", axis=1)
        )

        pindex_df = self.index_df.reset_index().set_index(["samplecode", "state"])
        join = pindex_df.join(pdf, how="left").dropna()

        return join

    def test_join_df(self) -> None:
        """
        Take the source df and join df and check whether the join is as expected. Specifically
        make sure that the relationship between the labels and series values has been maintained.

        Calculates the mean value of each series in both the base df and join_df then join
        the two on the mean column. Then checks for any mismatch by checking for NAs in
        result.
        """

        # calculate base df mean rounded to 10 digits and modify index to the 'mean' column
        df_means = (
            self.df.mean().to_frame("mean").round(10).reset_index().set_index("mean")
        )

        # calculate join df mean rounded to 10 digits and modify index to the 'mean' column
        post_join_means = (
            self.join_df.groupby(["samplecode", "wine", "state", "row", "col"])["mAU"]
            .apply(lambda df: df.mean().round(10))
            .to_frame(name="mean")
            .reorder_levels(["row", "col", "samplecode", "wine", "state"])
            .reset_index()
            .set_index("mean")
        )

        # join base df and join df on 'mean'
        mean_join = (
            post_join_means.join(
                df_means.loc[lambda df: ~(df.index.duplicated(keep="first"))],
                how="left",
                rsuffix="right",
                validate="many_to_one",
            )
            .reset_index()
            .set_index(["row", "col", "samplecode", "wine", "state"])
            .sort_index()
        )

        # test whether any NA in df, indicating a failed join. If assertion fails, outputs
        # rows with NA - use to identify mismatching join keys.
        assert ~mean_join.isna().all().all(), (
            "NAs in join, failed. Found in the"
            f" following\n{mean_join[mean_join.isna().any(axis=1)]}"
        )

    def build_relplot(self):
        self.join_df = (
            self.join_df.assign(mins=lambda df: df.mins.dt.total_seconds() / 60)
            .assign(
                col_label=lambda df: df.col.replace(
                    {
                        1: "query and ref",
                        2: "aligned and ref",
                        3: "query and aligned",
                    }
                )
            )
            .assign(
                col_label=lambda df: pd.Categorical(
                    values=df.col_label,
                    categories=[
                        "query and ref",
                        "aligned and ref",
                        "query and aligned",
                    ],
                    ordered=True,
                )
            )
            .reset_index()
            .set_index(["row", "col", "col_label", "samplecode", "state", "wine"])
        )

        relplot = sns.relplot(
            self.join_df,
            col="col_label",
            row="wine",
            x="mins",
            y="mAU",
            hue="state",
            kind="line",
            legend="full",
            facet_kws=dict(margin_titles=True, subplot_kws=dict(alpha=0.95)),
            errorbar=None,
            palette=sns.color_palette(n_colors=3, palette="colorblind"),
        ).set_titles(
            col_template="{col_name}",
            row_template="{row_name}",
        )
        relplot.fig.suptitle(
            "Comparison of Query and Reference Aligned Before and After DTW",
            fontsize=16,
        )
        relplot.fig.subplots_adjust(top=0.93)
