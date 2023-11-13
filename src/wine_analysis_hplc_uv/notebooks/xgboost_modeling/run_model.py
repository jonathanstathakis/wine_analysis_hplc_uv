import pandas as pd
import numpy as np
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import xgboost_model


def run_models():
    # declare parameters
    xgb_clf_params = dict(
        objective="multi:softprob",
        max_depth=3,
        alpha=10,
        gamma=10,
        eta=10,
        learning_rate=1,
        n_estimators=100,
        reg_alpha=10,
        # reg_lambda=10,
        tree_method="auto",
        random_state=42,
        verbosity=3,
        # optional parameter to control how impure a node should be to initiate a split. see <https://stats.stackexchange.com/questions/317073/explanation-of-min-child-weight-in-xgboost-algorithm#:~:text=The%20definition%20of%20the%20min_child_weight,will%20give%20up%20further%20partitioning.>
        # min_child_weight=0.01,
    )

    m = xgboost_model.MyModel()

    m.get_model_data()
    # # m.prep_for_model(enlarge_kwargs=dict(multiplier=4))

    # # m.grid_search(
    #     # get_grid_params()
    #     # )
    # # m.cv()
    m.model(
        # xgb_params=xgb_clf_params
    )
    m.display_results()

    # t = xgboost.testModel()
    # t.prep_for_model()
    # t.init_clf(cv_params)
    # t.cv()

    # t.model(
    # xgb_params=xgb_clf_params
    # )


def get_grid_params():
    """
    The following is a description of hyperparameter options relevant to XGBoost multiclass classification <https://www.kaggle.com/code/prashant111/a-guide-on-xgboost-hyperparameters-tuning>
    """
    return dict(
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


def main():
    run_models()


if __name__ == "__main__":
    main()
