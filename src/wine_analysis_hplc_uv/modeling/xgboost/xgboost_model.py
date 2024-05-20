from IPython.display import display
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from xgboost import XGBClassifier
from xgboost import plot_tree

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_validate
from sklearn import metrics
from imblearn import pipeline, over_sampling
import logging
from depreceated import depreceated

depreceated("approach is obsolete")

plt.style.use("ggplot")


logger = logging.getLogger(__name__)


class ModelMixin:
    def encode_data(self, y: pd.Series) -> pd.Series:
        """
        encode_data encode string classes to ordered numerical values

        Most models cant handle string labels, thus they needed to be encoded. This implementation uses sklearn LabelEncoder to transform the labels, but also store the transformation for later inversion. the encoder class can be accessed from `elf.le`.

        :param y: string labels to be encoded
        :type y: pd.Series
        :return: numerically encoded labels
        :rtype: pd.Series
        """
        logging.info("encoding y labels..")

        self.le = LabelEncoder()
        y = self.le.fit_transform(y)

        return y

    def split_data(
        self, X: pd.DataFrame, y: pd.DataFrame, test_size_: float = 0.2
    ) -> tuple:
        """
        split_data split dataset into training and test sets

        Training a ML model requires that the dataset is separated into training and test sets. This is accomplished through sklearn's `train_test_split`. Currently hardcoded for a `test_size` ratio of 0.2 of the total dataset size.

        :param X: The feature matrix
        :type X: pd.DataFrame
        :param y: the label array
        :type y: pd.Series
        :param test_size_: proportion ot the input dataset assigned to the test set
        :type test_size_: float
        :return: a tuple of `X_train`, `X_test`, `y_train`, and `y_test`, the split data according to `test_size`
        :rtype: tuple
        """
        logger.info("splitting the x and y into test and training sets..")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size_, random_state=42
        )
        return X_train, X_test, y_train, y_test

    def result_reports(
        self,
        y_test: np.ndarray,
        y_pred: np.ndarray,
        classes: np.ndarray,
        show: bool = True,
    ) -> None:
        """
        display_results display the confusion matrix and sklearn classification report

        :param y_test: the test set labels
        :type y_test: np.ndarray
        :param y_pred: the predicted labels from the test feature matrix
        :type y_pred: np.ndarray
        :param classes: the string labels corresponding to the encoded classes in the label arrays
        :type classes: np.ndarray
        :raises TypeError: if y_test is not a np.ndarray
        :raises TypeError: if y_pred is not a np.ndarray
        :raises TypeError: if classes is not a np.ndarray
        :return: None
        :rtype: None
        """

        if not isinstance(y_test, np.ndarray):
            raise TypeError(f"y_test must be pd.Series, got {type(y_test)}")

        if not isinstance(y_pred, np.ndarray):
            raise TypeError(f"y_pred must be pd.Series, got {type(y_pred)}")

        if not isinstance(classes, np.ndarray):
            raise TypeError(f"classes must be np.ndarray, got {type(classes)}")

        confm = pd.DataFrame(
            confusion_matrix(
                y_test,
                y_pred,
            ),
            index=classes,
            columns=classes,
        ).T

        classreport = pd.DataFrame(
            classification_report(
                y_test,
                y_pred,
                target_names=classes,
                output_dict=True,
            )
        )

        if show:
            display(confm)
            display(classreport)

        return confm, classreport


class XGBoostMixin:
    def init_clf(self, xgbclass_kwargs: dict = dict()) -> None:
        """
        init_clf initialise the XGBClassifier object

        Internally initializes an XGBClassifier object for sklearn Pipeline integration. Kwargs are supplied through `xgbclass_kwargs`. Returns None as the object is used internally.

        Link to docs: <https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBClassifier>

        :param xgbclass_kwargs: kwargs to initialize the XGBClassifier, defaults to dict()
        :type xgbclass_kwargs: dict, optional
        :raises TypeError: if `xgbclass_kwargs` is not a dict
        """

        if not isinstance(xgbclass_kwargs, dict):
            raise TypeError(
                f"xgbclass_kwargs must be dict, got {type(xgbclass_kwargs)}"
            )

        logger.info("Instantiating XGBClassifier..")

        # instantiate the classifier. Scikit-Learn API using inputted params
        clf = XGBClassifier(**xgbclass_kwargs)

        return clf

    def init_pipe(self, clf: XGBClassifier, smote_kwargs: dict = dict()) -> Pipeline:
        """
        init_pipe initalize a sklearn Pipeline with StandardScaler, PCA, and XGBClassifier supplied by the user. Returns the Pipeline object for downstream modeling

        Everything except for the XGBClassifier is hardcoded.

        :param clf: a previously initialized XGBClassifier
        :type clf: XGBClassifier
        :return: sklearn Pipeline object ready for modeling
        :rtype: Pipeline
        :raises TypeError: if `clf` is not `XGBClassifier`
        """

        if not isinstance(clf, XGBClassifier):
            raise TypeError(f"clf must be XGBClassifier, got {type(clf)}")

        logger.info("Initializing sklearn Pipeline..")

        xgbpipeline = pipeline.Pipeline(
            [
                (
                    "smote",
                    over_sampling.SMOTE(**smote_kwargs),
                ),
                ("scale", StandardScaler()),
                ("pca", PCA()),
                ("xgb", clf),
            ]
        )

        return xgbpipeline

    def plot_tree(self, clf: XGBClassifier) -> None:
        """
        plot_tree plot the fitted XGBoost Tree

        creates a graph plot of the fitted XGBoost Tree

        :param clf: The fitted XGBClassifer object
        :type clf: XGBClassifier
        :raises TypeError: if `clf` is not an XGBClassifier object
        """

        if not isinstance(clf, XGBClassifier):
            raise TypeError(f"clf must be XGBClassifier, got {type(clf)}")

        plot_tree(clf)

        return None


class XGBoostModeler(ModelMixin):
    """
    Syntax taken from: <https://www.kaggle.com/code/carlosdg/xgboost-with-scikit-learn-pipeline-gridsearchcv>
    use of 'roc_auc_ovr' taken from <https://stackoverflow.com/questions/31265110/does-gridsearchcv-not-support-multi-class>
    """

    def __init__(self):
        self._pro_data = None
        self.X, self.y = None, None
        self.X_train, self.X_test = None, None
        self.y_train, self.y_test, self.y_pred = None, None, None

        self.le = None
        self.clf = None
        self.pipe = None
        self.fit_model = None

    def prep_for_model(
        self,
        xgbclf_kwargs: dict = dict(),
        smote_kwargs: dict = dict(),
    ) -> tuple:
        """
        prep_for_model Prepare the sklearn Pipeline object and the training and test datasets

        Prepare the sklearn Pipeline object, initializing the XGBClassifier with `xgbclf_kwargs`, and split
        the dataset into training and test sets, X and y, respectively. Returns a tuple of the 4 data objects
        followed by the Pipeline object.

        :param xgbclf_kwargs: refer to [docs](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBClassifier), defaults to dict()
        :type xgbclf_kwargs: dict, optional
        :return: a tuple of (`X_train`,`X_test`,`y_train`, `y_test`, `pipe`)
        :rtype: tuple
        """
        (
            self.encode_y,
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test,
        ) = self.encode_and_split(self.X, self.y)

        self.pipe = self.prep_pipeline_classifier(
            xgbclf_kwargs=xgbclf_kwargs, smote_kwargs=smote_kwargs
        )

        return (
            self.encode_y,
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test,
            self.pipe,
        )

    def model(self) -> None:
        """
        model produce a single model without CV and display results

        Use for testing only.

        :param xgb_kwargs: kwargs for XGBClassifier, defaults to dict()
        :type xgb_kwargs: dict, optional
        """

        self.check_init()

        logger.info("Creating a single model..")

        # final data preparation. Renders the data non-human readable thus
        # for internal use only. Use le.inverse_transform() to go back to human readable encoding.

        logger.info("Fitting model..")

        self.fit_model = self.pipe.fit(self.X_train, self.y_train)

        logger.info(
            "Predicting x_test with fit model, storing results in self.y_pred.."
        )

        self.y_pred = self.fit_model.predict(self.X_test)

        return self.y_pred, self.pipe["xgb"]

    def gridsearch_CV(
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
    ) -> None:
        """ """

        """
        From :func:sklearn.model_selecton._search.GridSearchCV :
        - GridSearchCV automatically detects the classification problem type by the number of classes in `y`.
        - `cv` determines splitting strategy. Options are:
            - None: implements 5 fold.
            - Integer: number of folds in a (Stratified)KFold
            - Iterable yielding an array of indices as (train, test), i.e. a list
            - Note: if input is Integer or None, and problem is binary or multiclass, uses `StratifiedKFold`, else uses `KFold`. Both are used with `shuffle=False` so splits are the same.
            
        Ergo its using Stratified KFold BEFORE class balancing.
        """

        # use grid search with cross validation to find optimal hyperparameters

        grid = GridSearchCV(
            self.pipe,
            param_grid,
            cv=2,
            n_jobs=-1,
            scoring="roc_auc_ovr",
            # verbose=10,
            refit=True,
        )

        grid.fit(self.X, self.encode_y)

        # the following scores are generally considered the most appropriate for a multiclass problem
        scoring = dict(
            f1_macro=metrics.get_scorer("f1_macro"),
            precision_macro=metrics.get_scorer("precision_macro"),
            recall_macro=metrics.get_scorer("recall_macro"),
            balanced_acc=metrics.get_scorer("balanced_accuracy"),
        )

        # apply CV to the best estimator from the grid search with the scores defined above
        cv_output = cross_validate(
            grid.best_estimator_,
            self.X,
            self.encode_y,
            scoring=scoring,
            return_estimator=True,
        )

        # extract the scores of each fold
        scores = {key: cv_output[f"test_{key}"] for key in scoring.keys()}

        scores_df = pd.DataFrame.from_dict(scores)

        # define best estimator as the one with the highest average of the scores
        best_estimator_idx = scores_df.mean(axis=1).idxmax()
        best_estimator = cv_output["estimator"][best_estimator_idx]

        return scores_df, best_estimator

    def check_init(self) -> None:
        """
        check_init internal check to make sure that `prep_for_model` is called before modeling functions such as `model` or `grid_search`

        To enforce a process order, XGBoostModeler needs the dataset and pipe to be initialized by `prep_for_model`. Thus this function checks whether `X_train`, `X_test`, `y_train`, `y_test`, and `pipe` are initialized, and raises a ValueError if not.

        Note: because dataframes and series through an error if a None comparison is attempted, need to use `.empty`.

        :raises ValueError: if any of the objects are dataframes or series and are empty
        :raises ValueError: if any of the objects not dataframes or series are None
        """

        params_dict = dict(
            X_train=self.X_train,
            X_test=self.X_test,
            y_train=self.y_train,
            y_test=self.y_test,
            pipe=self.pipe,
        )

        for key, val in params_dict.items():
            if isinstance(val, (pd.DataFrame, pd.Series)):
                if val.empty:
                    raise ValueError(f"{key} is empty. Have you run `prep_for_model`?")
                else:
                    return None

        for key, val in params_dict.items():
            if not val:
                raise ValueError(
                    f"{key} has not been initialized. Have you run `prep_for_model`?"
                )
            else:
                return None

    def encode_and_split(self, X: pd.DataFrame, y: pd.Series):
        self.encode_y = self.encode_data(y)

        self.X_train, self.X_test, self.y_train, self.y_test = self.split_data(
            X, self.encode_y
        )

        return self.encode_y, self.X_train, self.X_test, self.y_train, self.y_test

    def prep_pipeline_classifier(
        self, xgbclf_kwargs: dict = dict(), smote_kwargs: dict = dict()
    ):
        self.clf = self.init_clf(xgbclf_kwargs)
        self.pipe = self.init_pipe(self.clf, smote_kwargs)

        return self.pipe
