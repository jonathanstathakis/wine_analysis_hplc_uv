"""
The methods for [2023-11-01-mcr_als_pipeline_prototype.ipynb](src/wine_analysis_hplc_uv/notebooks/mcr/2023-11-01-mcr_als_pipeline_prototype.ipynb)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.signal import savgol_filter
from scipy import signal
import seaborn.objects as so
import seaborn as sns
from pybaselines import Baseline
from sklearn import decomposition
import sys
import pymcr
import logging
import pymcr
from pymcr.regressors import OLS, NNLS
from wine_analysis_hplc_uv.signal_analysis.signal_analysis import SignalAnalyzer

scaler = StandardScaler()


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
        smoothed_col = df.groupby(grouper)[col].transform(
            lambda x: pd.Series(savgol_filter(x, **savgol_kws), index=x.index)
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

        out_df = df.assign(
            **dict(
                bline=lambda df: df.groupby(grouper)[col].transform(
                    lambda x: pd.Series(
                        Baseline(x.index).asls(x, **asls_kws)[0],
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

        df = df.assign(
            scale_center=lambda df: scaler.fit_transform(df[col].values.reshape(-1, 1))
        )

        return df


class PCA:
    def calculate_components(self, df):
        """
        Calculate the number of principal components in the dataset defined as the set of those containing greater than 0.0001 variance ratio.

        args

        df: an augmented dataframe with more rows than columns, i.e. observations x wavelengths
        """

        # initialise the PCA object and then fit transform on df
        pca = decomposition.PCA()
        pca.fit_transform(df)

        # construct a DataFrame of two columns: n = the number of components; and var_ratio = the variance ratio explained by that component

        screeplot_data = pd.DataFrame(
            dict(
                n=np.arange(pca.n_components_) + 1,
                var_ratio=pca.explained_variance_ratio_,
            )
        )

        # filter out components with less than 1E-3 variance ratio
        selected_components = screeplot_data.loc[lambda x: x.var_ratio > 1e-3]

        # display the selected components table
        display(selected_components)

        # create the scree plot, marking the last retained component
        screeplot_data.pipe(
            lambda x: so.Plot(data=x.loc[0:20], x="n", y="var_ratio")
            .add(so.Line())
            .add(
                so.Dot(marker="x"),
                data=selected_components.iloc[[-1]],
                x="n",
                y="var_ratio",
            )
        ).show()
        display()

        # number of components is equal to the number of rows of the selected_components table

        n_components = selected_components.shape[0]

        # display the nmber of components
        display(f"n components = {n_components}")

        return n_components


class SIMPLISMA:
    def simplisma(self, d, nr, error):
        def wmat(c, imp, irank, jvar):
            dm = np.zeros((irank + 1, irank + 1))
            dm[0, 0] = c[jvar, jvar]

            for k in range(irank):
                kvar = int(imp[k])

                dm[0, k + 1] = c[jvar, kvar]
                dm[k + 1, 0] = c[kvar, jvar]

                for kk in range(irank):
                    kkvar = int(imp[kk])
                    dm[k + 1, kk + 1] = c[kvar, kkvar]

            return dm

        nrow, ncol = d.shape

        dl = np.zeros((nrow, ncol))
        imp = np.zeros(nr)
        mp = np.zeros(nr)

        w = np.zeros((nr, ncol))
        p = np.zeros((nr, ncol))
        s = np.zeros((nr, ncol))

        error = error / 100
        mean = np.mean(d, axis=0)
        error = np.max(mean) * error

        s[0, :] = np.std(d, axis=0)
        w[0, :] = (s[0, :] ** 2) + (mean**2)
        p[0, :] = s[0, :] / (mean + error)

        imp[0] = int(np.argmax(p[0, :]))
        mp[0] = p[0, :][int(imp[0])]

        l = np.sqrt((s[0, :] ** 2) + ((mean + error) ** 2))

        for j in range(ncol):
            dl[:, j] = d[:, j] / l[j]

        c = np.dot(dl.T, dl) / nrow

        w[0, :] = w[0, :] / (l**2)
        p[0, :] = w[0, :] * p[0, :]
        s[0, :] = w[0, :] * s[0, :]

        print("purest variable 1: ", int(imp[0] + 1), mp[0])

        for i in range(nr - 1):
            for j in range(ncol):
                dm = wmat(c, imp, i + 1, j)
                w[i + 1, j] = np.linalg.det(dm)
                p[i + 1, j] = w[i + 1, j] * p[0, j]
                s[i + 1, j] = w[i + 1, j] * s[0, j]

            imp[i + 1] = int(np.argmax(p[i + 1, :]))
            mp[i + 1] = p[i + 1, int(imp[i + 1])]

            print(
                "purest variable " + str(i + 2) + ": ", int(imp[i + 1] + 1), mp[i + 1]
            )

        sp = np.zeros((nrow, nr))

        for i in range(nr):
            sp[0:nrow, i] = d[0:nrow, int(imp[i])]

        plt.subplot(3, 1, 2)
        plt.plot(sp)
        plt.title("Estimate Components")

        concs = np.dot(np.linalg.pinv(sp), d)

        plt.subplot(3, 1, 3)
        for i in range(nr):
            plt.plot(concs[i])
        plt.title("Concentrations")
        plt.show()

        return sp, concs


class MCR_ALS:
    def mcr_als(self, D, S, mcr_als_kws: dict = dict(), mcr_als_fit_kws: dict = dict()):
        """
        A wrapper for pymcr.mcr.McrAR. Returns the mcrar object.

        args

        D: Augmented data matrix with observations as rows and wavelengths as columns
        S: estimate spectral matrix
        mcr_als_kws: initialization keywords
        mcr_als_fit_kws: fit method keywords

        See: [pyMCR](https://github.com/usnistgov/pyMCR)
        """
        mcrar = pymcr.mcr.McrAR(**mcr_als_kws)
        mcrar.fit(D=D, ST=S.T, **mcr_als_fit_kws)

        return mcrar


class MCR_Analysis(SIMPLISMA, PCA, MCR_ALS, SignalAnalyzer):
    def __init__(self):
        return None
