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


class XGBoostModeling:

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

        self.fit_model = self.pipeline.fit(self.X_train, self.y_train)

        logger.info(
            "Predicting x_test with fit model, storing results in self.y_pred.."
        )

        self.y_pred = self.fit_model.predict(self.X_test)

        self.display_results()

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

        self.get_model_data()
        self.encode_data()
        self.split_data()

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

        grid.fit(self.X_train, self.y_train)
        display(f"mean test score: {grid.cv_results_['mean_test_score']}")
        display(grid.best_estimator_)
        display(grid.best_params_)

        best_pipe_clf = grid.best_estimator_
        self.y_pred = best_pipe_clf.predict(self.X_test)

        display(classification_report(self.y_test, self.y_pred))

        plot_tree(best_pipe_clf["xgb"])

    def encode_data(self):
        logging.info("encoding y labels..")

        self.le = LabelEncoder()
        self.y = self.le.fit_transform(self.y)

    def split_data(self):
        logger.info("splitting the x and y into test and training sets..")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )

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
    def __init__(self):
        datasets.MyData.__init__(self, db_path=definitions.DB_PATH)
        self.X, self.y = None, None

    def run_ETL_pipeline(self):
        append = True

        process_frame_kwargs = dict(
            resample_kwgs=dict(
                grouper=["id", "code_wine"],
                time_col="mins",
                original_freqstr="0.4S",
                resample_freqstr="2S",
            ),
            melt_kwgs=dict(
                id_vars=["detection", "color", "varietal", "id", "code_wine", "mins"],
                value_name="signal",
                var_name="wavelength",
            ),
            smooth_kwgs=dict(
                smooth_kwgs=dict(
                    grouper=["id", "wavelength"],
                    col="signal",
                ),
                append=append,
            ),
            bline_sub_kwgs=dict(
                prepro_bline_sub_kwgs=dict(
                    grouper=["id", "wavelength"],
                    col="smoothed",
                    asls_kws=dict(max_iter=100, tol=1e-3, lam=1e5),
                ),
                append=append,
            ),
            pivot_kwgs=dict(
                columns=["detection", "color", "varietal", "id", "code_wine"],
                index="mins",
                values="bcorr",
            ),
        )

        model_prep_kwargs = dict(
            target_col="varietal",
            drop_cols=[
                "color",
                "detection",
                "id",
                "code_wine",
            ],
            min_class_size=6,
        )

        self.model_pipeline(
            process_frame_kwargs=process_frame_kwargs,
            model_prep_kwargs=model_prep_kwargs,
        )


class testModel(datasets.TestData, XGBoostModeling):
    def __init__(self):
        datasets.TestData.__init__(self)
