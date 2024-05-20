import pandas as pd
from scipy import signal
from sklearn import preprocessing
import pybaselines
import logging
from deprecated import deprecated

# TODO: identify where the current signal processing module is
deprecated(
    reason="this is an obsolete module as the approach to signal processing has changed"
)
logger = logging.getLogger(__name__)


class Preprocessing:
    def _smooth(
        self,
        df,
        grouper: str,
        col: str,
        savgol_kws: dict = dict(window_length=5, polyorder=2),
    ):
        """
        Smooth the signal with savgol filter.

        args:

        df: long format dataframe with a group label column
        grouper: column containing the labels of the groups to iterate over
        smoothed_colname: name of the output column
        savgol_kws: refer to scipy.signal.savgol_filter
        """

        logger.info(
            f"Smoothing {col} in supplied df grouped by {grouper} with {savgol_kws}.."
        )

        smoothed_col = df.groupby(grouper)[col].transform(
            lambda x: pd.Series(signal.savgol_filter(x, **savgol_kws), index=x.index)
        )

        return smoothed_col

    def _baseline_subtract(
        self,
        df,
        col: str,
        grouper: str | list[str],
        asls_kws: dict = dict(max_iter=50, tol=1e-3, lam=1e6),
    ):
        """
        Baseline subtract

        args:

        df - long df with wavelengths as an id col.
        col - target column to be transformed
        grouper - column containing the group labels, i.e. wavelengths
        baseline_corrected_name - the name of the newly created column
        """

        logger.info(
            f"Subtracting baseline from {col} of df grouped by {grouper} with {asls_kws}.."
        )

        out_df = df.assign(
            **dict(
                bline=lambda df: df.groupby(grouper)[col].transform(
                    lambda x: pd.Series(
                        pybaselines.Baseline(x.index).asls(x, **asls_kws)[0],
                        index=x.index,
                    ).where(lambda x: x > 0, 0)
                )
            )
        )
        bcorr = out_df.eval(f"{col}-bline")
        return bcorr

    def subset(self, df, index, limit):
        """
        subset to a range between origin and 'limit'

        args:

        df: long form df with a column that can act as an index
        index: the column defining the range to be subset on
        limit: the last value of the index column to be included in the range
        """
        df = df.loc[df[index] < limit]

        return df

    def scale_and_center(self, df, col: str):
        # scale and center

        scaler = preprocessing.StandardScaler()

        df = df.assign(
            scale_center=lambda df: scaler.fit_transform(df[col].values.reshape(-1, 1))
        )

        return df
