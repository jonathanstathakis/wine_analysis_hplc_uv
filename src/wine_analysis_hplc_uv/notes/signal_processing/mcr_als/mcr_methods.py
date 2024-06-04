"""
The methods for [2023-11-01-mcr_als_pipeline_prototype.ipynb](src/wine_analysis_hplc_uv/notebooks/mcr/2023-11-01-mcr_als_pipeline_prototype.ipynb)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import seaborn.objects as so
from sklearn import decomposition


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

        # number of components is equal to the number of rows of the selected_components table

        n_components = selected_components.shape[0]

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

        l_ = np.sqrt((s[0, :] ** 2) + ((mean + error) ** 2))

        for j in range(ncol):
            dl[:, j] = d[:, j] / l_[j]

        c = np.dot(dl.T, dl) / nrow

        w[0, :] = w[0, :] / (l_**2)
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


# class MCR_ALS:
#     def mcr_als(self, D, S, mcr_als_kws: dict = dict(), mcr_als_fit_kws: dict = dict()):
#         """
#         A wrapper for pymcr.mcr.McrAR. Returns the mcrar object.

#         args

#         D: Augmented data matrix with observations as rows and wavelengths as columns
#         S: estimate spectral matrix
#         mcr_als_kws: initialization keywords
#         mcr_als_fit_kws: fit method keywords

#         See: [pyMCR](https://github.com/usnistgov/pyMCR)
#         """
#         mcrar = pymcr.mcr.McrAR(**mcr_als_kws)
#         mcrar.fit(D=D, ST=S.T, **mcr_als_fit_kws)

#         return mcrar


# class MCR_Analysis(SIMPLISMA, PCA, MCR_ALS, SignalAnalyzer):
#     def __init__(self):
#         return None
