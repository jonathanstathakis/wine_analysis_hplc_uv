from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import datasets, xgboost_model
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_prep
from dataclasses import dataclass
import matplotlib.pyplot as plt


class RawRedModel(
    datasets.RawRedData, xgboost_model.XGBoostModeler, data_prep.DataPrepper
):
    def __init__(self):
        datasets.RawRedData.__init__(self, db_path=definitions.DB_PATH)
        xgboost_model.XGBoostModeler.__init__(self)
        self.kwargs = Kwargs()

    def run_model(self, model_type: str = "single", param_grid=dict()) -> None:
        """
        since grid search, CV and single model implementations all share a common prepartory stage, and a common result display (if gridsearch is an intermediate before CV) it makes sense to have an intermediate function that then summons the desired behavior. Options:
        'single' - single model
        'CV' - perform CV
        'gridsearchCV' - perform a grid search then CV with the best estimator
        """

        self.extract_signal_process_pipeline(
            self.kwargs.extract_signal_process_pipeline_kwargs
        )

        self.X, self.y = self.transform_dataset(
            data=self.pro_data_, **self.kwargs.transform_dataset_kwargs
        )

        self.prep_for_model(self.kwargs.xgbclf_kwargs)

        if model_type == "single":
            y_pred, clf = self.model()

        if model_type == "gridCV":
            scores_df, best_est = self.gridsearch_CV()

        print(scores_df)
        self.plot_tree(best_est["xgb"])
        plt.show()

        return scores_df, best_est


@dataclass
class Kwargs:
    append = True

    extract_signal_process_pipeline_kwargs = dict(
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

    transform_dataset_kwargs = dict(
        target_col="varietal",
        drop_cols=[
            "color",
            "detection",
            "id",
            "code_wine",
        ],
        min_class_size=6,
    )

    xgbclf_kwargs = dict()

    grid_param_kwargs = dict(
        # choose the booster
        xgb__booster=["dart"],
        # the following are tree booster params
        # eta [default=0.3, alias=learning_rate]
        # range 0-1
        # typical values 0.01-0.2
        # same as learning rate. Decrease reduces
        # overfitting
        xgb__eta=[0.01, 0.05, 1, 1.5, 2, 2.5, 3],
        # gamma [default=0, alias: min_split_loss]
        # specifies minimum loss reduction to initiate a split. Larger means more conservative
        # range: [0,inf]
        # typical vals: missing
        xgb__gamma=[0, 0.5, 2, 10],
        # max_depth: [default=6]
        # maximum depth of a tree
        # deeper trees more overfit
        # range [0,inf]
        # typical vals: 3-10
        xgb__max_depth=[2, 5, 7, 10],
        # min_child_weight: [defualt=1]
        # minimum sum of weights required in a child
        # higher values promote underfitting
        # range: [0,inf]
        # typical vals: missing
        xgb__min_child_weight=[0, 0.01, 0.5, 1, 2],
        # scale_pos_weight
        # controls balance of positive and negative weights, useful for imbalanced classes
        # >0 should be used in cases of high imbalance to produce faster convergence
        # typical val: sum(negative instances)/sum(positive instances)
        # xgb__scale_pos_weight=[0,0.2,0.5,0.7,1]
    )


class testModel(datasets.TestData, xgboost_model.XGBoostModeler):
    def __init__(self):
        datasets.TestData.__init__(self)
