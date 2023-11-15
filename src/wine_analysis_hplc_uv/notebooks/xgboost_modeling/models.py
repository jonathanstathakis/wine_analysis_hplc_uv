from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import datasets, xgboost_model
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_prep
from dataclasses import dataclass
import matplotlib.pyplot as plt
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import kwarg_classes


class ModelBasis(xgboost_model.XGBoostModeler, data_prep.DataPrepper):
    def __init__(self):
        xgboost_model.XGBoostModeler.__init__(self)
        self.kwargs = DefaultKwargs()

    def run_model(self, model_type: str = "single", param_grid=dict()) -> None:
        """
        since grid search, CV and single model implementations all share a common prepartory stage, and a common result display (if gridsearch is an intermediate before CV) it makes sense to have an intermediate function that then summons the desired behavior. Options:
        'single' - single model
        'CV' - perform CV
        'gridsearchCV' - perform a grid search then CV with the best estimator
        """

        self.X, self.y = self.transform_dataset(
            data=self.pro_data_, **self.kwargs.transform_dataset_kwargs
        )

        self.prep_for_model(self.kwargs.xgbclf_kwargs, self.kwargs.smote_kwargs)

        if model_type == "single":
            y_pred, clf = self.model()

        if model_type == "gridCV":
            scores_df, best_est = self.gridsearch_CV(
                param_grid=self.kwargs.grid_param_kwargs
            )

        print(scores_df)
        self.plot_tree(best_est["xgb"])
        plt.show()

        return scores_df, best_est


class RawRedVarietalModel(ModelBasis, datasets.RawRedVarietalData):
    def __init__(self):
        datasets.RawRedVarietalData.__init__(
            self,
            db_path=definitions.DB_PATH,
            ext_kwargs=kwarg_classes.DefaultETKwargs().extractor_kwargs,
            dp_kwargs=kwarg_classes.DefaultETKwargs().data_pipeline_kwargs,
        )
        self.kwargs = kwarg_classes.RawRedVarietalKwargs()


class CUPRACRedVarietalModel(ModelBasis, datasets.CUPRACRedVarietalData):
    def __init__(self):
        datasets.CUPRACRedVarietalData.__init__(self, db_path=definitions.DB_PATH)
        self.kwargs = CUPRACRedVarietalKwargs()


class testModel(datasets.TestData, xgboost_model.XGBoostModeler):
    def __init__(self):
        datasets.TestData.__init__(self)
