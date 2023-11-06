"""
2023-11-05

XGBoost. Get it done.

- [x] get the data in memory
- [ ] build the model
- [ ] analyse results

2023-11-05 18:56:37 - need to unpivot so that 'code_wine' and 'id' are labels and 'varietal' is a column

2023-11-06 08:50:20 - start with a 2 class problem, pinot noir vs shiraz. There are 11 of each in the dataset. Start with that then build up.

2023-11-06 09:28:41 - # recommended to use the scikit learn API: <https://www.kaggle.com/code/bextuychiev/20-burning-xgboost-faqs-answered-to-use-like-a-pro>

2023-11-06 09:48:38 - From wikipedia:

Multiclass classification solutions can be divided into one - vs. -rest (OvR) and one vs. one (OvO). OvR trains a classifier per class, OvO trains (K(K-1)/2), where K is the number of classes in the training set, and the classifiers are trained on pairs of classes from the training set.

2023-11-06 10:19:58 - Multiclass classification accuracy measures:

- Accuracy
- precision
- true positives
- true negatives
- false positives
- false negatives


<https://www.evidentlyai.com/classification-metrics/multi-class-metrics>:
- Accuracy is (correct predictions)/(all predictions)


2023-11-06 10:25:08 - problem 1: how to measure results?

2023-11-06 10:57:45 - all of the classifiers are producing the same mlogloss value of 0.69.., which is v. sus. To solve this im going to recreate a kaggle notebook with a similar problem and test my pipeline on that. Note that since im using a OOP pipeline, ive constructed it such that data acquisition and processing is seperate from modeling so that it swapping datasets should be straightforeward.

2023-11-06 11:50:23 - ok, for the iris set we're getting a 89% prediction accuracy. Now plug my dataset back in.

2023-11-06 12:18:12 - My trees are not building as expected, indicated by the lack of prediction variation. It is probably to do with how small the dataset size is vs the number of predictors, i.e. $p>>n$ where $p$ is columns and $n$ is rows.

Before looking into strategies to handle this, apply PCA to get the first x components and try modeling that. Strategies can be found at <https://machinelearningmastery.com/how-to-handle-big-p-little-n-p-n-in-machine-learning/>

2023-11-06 12:50:53 - working with dimensional data, $p>>n$ <https://carpentries-incubator.github.io/high-dimensional-stats-r/01-introduction-to-high-dimensional-data/index.html>

2023-11-06 13:11:34 - need to fit transformers to the train set distributions then transform both the train set and test set with that transformer instance seperately in order to have both sets in the same domain but avoid data leakage.

2023-11-06 13:12:30 - Even after PCA transformation reducing the set to 21 features we're getting the same results, an array of zeroes, meaning that all samples in the test set are always being predicted as pinot noir. what if we like.. triple the size of the dataset.

"""

# initialization

import os
import pandas as pd
import numpy as np
import seaborn.objects as so
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn import decomposition
from IPython.display import display
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


label_cols = ["varietal", "code_wine", "id"]


class MyData:
    def __init__(self):
        self.target_col = "varietal"
        self.label_cols = ["varietal", "code_wine", "id"]
        self.cols_to_drop = ["id", "code_wine"]

        self.data = self.get_dset()
        self.x, self.y = self.prep_for_model()

    def get_dset(self):
        path = os.path.join(
            "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/pca-xgboost/pca_dset.parquet"
        )

        data = pd.read_parquet(path)
        data = data.T.reset_index()

        return data

    def enlarge_dataset(self):
        """
        Artifically increasing the size of the dataset to see if that affects model as of
        2023-11-06 13:15:22 I am getting the same predictions every run
        """
        display(self.data.shape)

        for i in range(2):
            self.data = pd.concat([self.data, self.data])
            display(self.data.shape)

    def select_dataset_size(self, min_num_samples):
        """
        Subset the dataset size based on how many samples in a given class
        """
        var_labels = (
            self.data.varietal.value_counts().loc[lambda x: x >= min_num_samples].index
        )

        self.data = self.data.loc[lambda df: df.varietal.isin(var_labels)]

    def prep_for_model(self):
        # selects for pinot noir and shiraz varietals only, both with 11 members currently 2023-11-06.

        self.select_dataset_size(6)

        self.enlarge_dataset()

        # plots the signals
        # display(data.drop(['varietal','code_wine','id'], axis=1).T.plot(legend=False))

        x = self.data.drop([self.target_col] + self.cols_to_drop, axis=1)

        y = self.data.loc[:, self.target_col]

        return x, y


class TestData:
    def __init__(self):
        self.data = self.getdata()
        self.x, self.y = self.prep_for_model(self.data)

    def getdata(self):
        # get the iris dataset and prep it to resemble my dataset
        data = datasets.load_iris()
        df = pd.DataFrame(data=data.data, columns=data.feature_names)
        df["target"] = data.target
        df.target = df.target.replace(
            {0: data.target_names[0], 1: data.target_names[1], 2: data.target_names[2]}
        )

        return df

    def prep_for_model(self, data):
        X = data.drop("target", axis=1)
        y = data.target

        return X, y


class PCA_Transformation:
    """
    2023-11-06 12:35:46

    Preprocessing should be done AFTER splitting otherwise there is data leakage through
    the distribution. Refer to <https://stackoverflow.com/questions/45639915/split-x-into-test-train-before-pre-processing-and-dimension-reduction-or-after>
    """

    def scale_x(self, x_train, x_test):
        """
        Apply this to the x_train and x_test sets are splitting
        """
        scaler = StandardScaler()
        scaled_x_train = scaler.fit_transform(x_train)
        scaled_x_test = scaler.transform(x_test)

        return scaled_x_train, scaled_x_test

    def apply_pca(self, x_train, x_test):
        scaled_x_train, scaled_x_test = self.scale_x(x_train, x_test)

        pca = PCA()

        pca.fit(X=scaled_x_train)

        # transformed x
        tf_x_train = pca.fit_transform(scaled_x_train)
        tf_x_test = pca.transform(scaled_x_test)

        return tf_x_train, tf_x_test


class XGBoostModeling(PCA_Transformation):
    def prep_data(self):
        self.encode_data()
        self.split_data()
        self.pca_decomp()

    def encode_data(self):
        self.le = LabelEncoder()
        self.y = self.le.fit_transform(self.y)

    def split_data(self):
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y
        )

    def pca_decomp(self):
        self.x_train, self.x_test = self.apply_pca(self.x_train, self.x_test)

    def train_model(self):
        # declare parameters
        params = dict(
            objective="multi:softprob",
            max_depth=6,
            alpha=10,
            learning_rate=1.0,
            n_estimators=100,
            tree_method="auto",
            random_state=42,
            num_class=2,
        )

        # instantiate the classifier. Scikit-Learn API
        xgb_clf = XGBClassifier(**params)

        # fit the classifier to the training data

        fit_params = dict(
            # eval_set=[(self.x_train, self.y_train),(self.x_test,self.y_test)],
            verbose=False
        )

        self.model = xgb_clf.fit(self.x_train, self.y_train, **fit_params)

        # make a prediction on the test set. If xgboost autodetects a binary class
        # problem (only 2 classes in the targets) it returns the probability for each
        # class(?) a 2d array for each sample, otherwise a 1d array with the prediction

        self.y_pred = self.model.predict(self.x_test)

        # calculate the accuracy score of the test targets vs the predicted targets
        display(accuracy_score(self.y_test, self.y_pred))

        display(self.le.inverse_transform(self.y_pred))

    def see_results(self, model, data_dict):
        # compute and print accuracy score

        from sklearn.metrics import confusion_matrix

        y_pred = model.predict(data_dict["X_test"])


class MyModel(MyData, XGBoostModeling):
    def __init__(self):
        MyData.__init__(self)


class testModel(TestData, XGBoostModeling):
    def __init__(self):
        TestData.__init__(self)


def main():
    m = MyModel()
    t = testModel()
    pca = PCA_Transformation()

    m.prep_data()
    m.train_model()

    t.prep_data()
    t.train_model()

    display


if __name__ == "__main__":
    main()
