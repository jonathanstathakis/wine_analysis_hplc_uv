from dataclasses import dataclass


@dataclass
class DefaultETKwargs:
    append = True

    extractor_kwargs = dict(
        detection=("raw",),
        exclude_ids=("6d8a370a-9f40-460d-acba-99fd4c287ad8",),
        wavelengths=(256,),
        color=("red",),
        mins=(0, 30),
    )

    data_pipeline_kwargs = dict(
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


@dataclass
class DefaultModelKwargs:
    append = True

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

    smote_kwargs = dict(k_neighbors=2, sampling_strategy={0: 22, 1: 22, 2: 22})

    grid_param_kwargs = dict(
        # choose the booster
        xgb__booster=["dart"],
        # the following are tree booster params
        # eta [default=0.3, alias=learning_rate]
        # range 0-1
        # typical values 0.01-0.2
        # same as learning rate. Decrease reduces
        # overfitting
        xgb__eta=[0.05, 1, 1.5, 2, 2.5, 3],
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
        xgb__min_child_weight=[0.01, 0.5, 1, 2],
        # scale_pos_weight
        # controls balance of positive and negative weights, useful for imbalanced classes
        # >0 should be used in cases of high imbalance to produce faster convergence
        # typical val: sum(negative instances)/sum(positive instances)
        # xgb__scale_pos_weight=[0,0.2,0.5,0.7,1]
    )


class RawRedVarietalETKwargs(DefaultETKwargs):
    pass


class RawRedVarietalModelKwargs(DefaultModelKwargs):
    pass


class CUPRACRedVarietalETKwargs(DefaultETKwargs):
    extractor_kwargs = dict(
        detection=("cuprac",),
        exclude_ids=("6d8a370a-9f40-460d-acba-99fd4c287ad8",),
        wavelengths=(450,),
        color=("red",),
        mins=(0, 30),
    )


class CUPRACRedVarietaModelKwargs(DefaultModelKwargs):
    transform_dataset_kwargs = dict(
        target_col="varietal",
        drop_cols=[
            "color",
            "detection",
            "id",
            "code_wine",
        ],
        min_class_size=5,
    )
    pass
