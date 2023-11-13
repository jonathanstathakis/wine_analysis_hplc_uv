"""
2023-11-05

XGBoost. Get it done.

- [x] get the data in memory
- [x] build the model
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

2023-11-06 13:12:30 - Even after PCA transformation reducing the set to 21 features we're getting the same results, an array of zeroes, meaning that all samples in the test set are always being predicted as pinot noir. what if we like.. double the size of the dataset.

2023-11-06 13:34:41 - duplicating the samples in my dataset of 'pinot noir', 'red_bordeaux blend', and 'shiraz' has produced a result! also, after multiple runs it appears to achieve a +70% accuracy. Not shabby for a first run. Now to instantiate a cross-validation to produce average performance scores, and see if we can explain why that worked. Note, removing the pca decomposition produces accuracy scores of +90%. We're overfitting so hard.

2023-11-06 13:43:39 - reducing the class size threshold to two which introduces 15 classes, for some reason the accuracy drops to 0.06 and all test samples are classified as CS even though its one of the smallest classes sizes. Weird. Going to three reduces the number of classes to 9, 

2023-11-06 13:59:03 - to implement CV with preprocessing, best way to do it is with scikit-learn pipelines. Will refactor the preprocessing to that API now.

2023-11-06 14:44:50 - I am getting absurdly high results both in and out of the pipeline, so I think it might be accurate for the dataset..

2023-11-06 14:47:04 - the manipulation of occurances of samples in the dataset is referred to as oversampling (as a verb) the opposite action - removing samples, is called undersampling. <https://www.techtarget.com/whatis/definition/over-sampling-and-under-sampling#:~:text=Over%20sampling%20is%20used%20when,occurrences%20in%20the%20minority%20class.> says that SMOTE is an approach to oversampling by cloning samples by feature distribution rather than direct duplication, apprently better.

2023-11-06 16:26:15 - `cross_validate` is the one to use, allows custom score selection amongst other options.

2023-11-06 16:28:22 - regarding the 0.5 result for the original dset, this post <https://datascience.stackexchange.com/questions/112642/why-xgboost-does-not-work-on-small-dataset> has the same result for a 1 feature dataset. Reply says `min_child_weight` modification helps. Says its happening because the model cant split the trees properly.

2023-11-06 17:46:28 - a range of 'min_child_weight' values had no effect on the outcome.
2023-11-06 19:23:46 - after initial broad grid search, still no effective splitting on the basic size dataset. Q: is total dataset size or class sizes?

2023-11-07 08:33:58 - Have found that there are no trees grown for a range of hyperparameter settings, so we're now looking for references to solve this problem. Need to find a combination of hyperparameters which enable splitting. <https://www.kaggle.com/code/rafjaa/dealing-with-very-small-datasets> recommends restricting max depth, increasing values of gamma, `eta`, `reg_alpha`, and `reg_lambda`

2023-11-07 09:22:04 - from <https://towardsai.net/p/l/multi-class-model-evaluation-with-confusion-matrix-and-classification-report> and <https://datascience.stackexchange.com/questions/15989/micro-average-vs-macro-average-performance-in-a-multiclass-classification-settin>:

- 'Micro' metrics refer to calculations of performance without consideration for the class the sample belongs to, then 'aggregating' the results (?)
- 'Macro' is unweighted mean of the measure for each class, taking the measurement within each class then averaging across classes
- 'Weighted' refers to accounting for the number of samples in a class when making measurements

For sets with class imbalance it is recommended to use 'micro' scores        

2023-11-07 10:00:04 - I have established methods of producing a easy-to-read pandas dataframe confusion matrix and classification report, and plot of the tree.

2023-11-13 09:22:38 - multiclass confusion matrix displays the expected values as columns and predicted values as rows. The values are the number of samples in that location, Where the diagonal is TP <https://www.v7labs.com/blog/confusion-matrix-guide#confusion-matrix-for-multiple-classes>
"""

# initialization

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline

from IPython.display import display

import os

import pandas as pd
import numpy as np

import seaborn as sns
import seaborn.objects as so
import matplotlib as mpl
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

from xgboost import XGBClassifier
from xgboost import plot_tree

from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_validate
from sklearn.model_selection import cross_val_predict
from sklearn import decomposition

from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import datasets

plt.style.use("ggplot")

import logging

logging_level = logging.INFO
logger = logging.getLogger()
logger.setLevel(logging_level)

formatter = logging.Formatter(
    "%(asctime)s %(name)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(stream_handler)


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

    """
    Syntax taken from: <https://www.kaggle.com/code/carlosdg/xgboost-with-scikit-learn-pipeline-gridsearchcv>
    use of 'roc_auc_ovr' taken from <https://stackoverflow.com/questions/31265110/does-gridsearchcv-not-support-multi-class>

    """

    def init_pipe(self, clf):
        """
        Initialize the Pipeline object
        """

        logger.info("Initializing sklearn Pipeline..")

        self.pipeline = Pipeline(
            [("scaling", StandardScaler()), ("reduce_dim", PCA()), ("xgb", clf)]
        )

        return self.pipeline

    def model(self, xgb_params: dict = dict()):
        """
        produce a single model
        """

        logger.info("Creating a single model..")

        self.encode_data()

        self.split_data()

        self.init_clf(xgb_params)

        self.init_pipe(self.clf)

        logger.info("Fitting model..")

        self.fit_model = self.pipeline.fit(self.x_train, self.y_train)

        logger.info(
            "Predicting x_test with fit model, storing results in self.y_pred.."
        )

        self.y_pred = self.fit_model.predict(self.x_test)

    def display_results(self):
        display(
            pd.DataFrame(
                confusion_matrix(
                    self.y_test,
                    self.y_pred,
                ),
                index=self.le.classes_,
                columns=self.le.classes_,
            ).T
        )

        display(
            pd.DataFrame(
                classification_report(
                    self.y_test,
                    self.y_pred,
                    target_names=self.le.classes_,
                    output_dict=True,
                )
            )
        )
        plot_tree(self.clf)

    def grid_search(
        self,
        param_grid: dict = dict(
            xgb__objective=["multi:softprob"],
            xgb__max_depth=[6],
            xgb__alpha=[10],
            xgb__learning_rate=[0.5, 1.0],
            xgb__n_estimators=[50, 100],
            xgb__tree_method=["auto"],
            xgb__random_state=[42],
        ),
    ):
        """
        Perform grid search. Syntax taken from <https://www.mygreatlearning.com/blog/gridsearchcv/>

        docs:<https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>
        """

        self.prep_data()

        pipe = self.init_pipe(clf=XGBClassifier())

        grid = GridSearchCV(
            self.pipeline,
            param_grid,
            cv=5,
            n_jobs=-1,
            scoring="roc_auc_ovr",
            verbose=10,
            refit=True,
        )

        grid.fit(self.x_train, self.y_train)
        display(f"mean test score: {grid.cv_results_['mean_test_score']}")
        display(grid.best_estimator_)
        display(grid.best_params_)

        best_pipe_clf = grid.best_estimator_
        self.y_pred = best_pipe_clf.predict(self.x_test)

        display(classification_report(self.y_test, self.y_pred))

        plot_tree(best_pipe_clf["xgb"])

    def cv(self, xgb_params: dict = dict()):
        assert isinstance(self.x, (pd.DataFrame, np.ndarray))
        assert isinstance(self.y, (pd.Series, np.ndarray)), f"{type(self.y)}"

        self.init_clf(params=xgb_params)

        display(
            pd.DataFrame(
                cross_validate(
                    estimator=self.init_pipe(self.clf),
                    X=self.x,
                    y=self.y,
                    scoring=[
                        "f1_macro",
                        "accuracy",
                    ],
                )
            )
        )

    def encode_data(self):
        logging.info("encoding y labels..")

        self.le = LabelEncoder()
        self.y = self.le.fit_transform(self.y)

    def split_data(self):
        logger.info("splitting the x and y into test and training sets..")
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y, test_size=0.2, random_state=42
        )

    def pca_decomp(self):
        self.x_train, self.x_test = self.apply_pca(self.x_train, self.x_test)

    def init_clf(self, params: dict = dict()):
        """
        Initialise the XGBoost Classifier through the Scikit-Learn API with provided
        parameters.

        Link to docs: <https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBClassifier>
        """

        logger.info("Instantiating XGBClassifier..")

        # instantiate the classifier. Scikit-Learn API using inputted params
        self.clf = XGBClassifier(**params)


class MyModel(datasets.MyData, XGBoostModeling):
    def __init__(self, target_col: str, label_cols=list, drop_cols=list):
        datasets.MyData.__init__(
            self, target_col=target_col, label_cols=label_cols, drop_cols=drop_cols
        )


class testModel(datasets.TestData, XGBoostModeling):
    def __init__(self):
        TestData.__init__(self)
