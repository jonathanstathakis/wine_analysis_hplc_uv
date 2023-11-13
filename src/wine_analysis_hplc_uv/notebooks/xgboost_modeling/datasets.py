import logging

logger = logging.getLogger(__name__)

from sklearn import datasets

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract

import pandas as pd


class ModelPrepper:
    def prep_for_model(
        self,
        data: pd.DataFrame,
        target_col: str,
        drop_cols: str | list,
        enlarge_kwargs: dict = dict(),
        min_class_size: int | float = 1,
    ) -> tuple:
        """
        Take a dataframe and prepare it for model building

        Intended to be used on the output of `DataPipeline.process_frame`, take a tidy
        format frame with samples as columns and observations as rows and return
        a tuple of a feature matrix and label array (DataFrame and Series).

        :param data: tidy format dataframe with columns as samples and rows as observations
        :type data: pd.DataFrame
        :param target_col: The column of data containing the classification target labels
        :type target_col: str
        :param drop_cols: superfluous columns to be excluded from the output
        :type drop_cols: str | list
        :param enlarge_kwargs: kwargs for `ModelPrepper.enlarge_dataset`, defaults to dict()
        :type enlarge_kwargs: dict, optional
        :param min_class_size: minimum class size required to be included in input dataset, defaults to 1
        :type min_class_size: int | float, optional
        :return: returns a tuple of (x, y) where targets are in y and features are in x
        :rtype: tuple (pd.DataFrame, pd.Series)
        """
        # orient frame with labels and observations as columns, samples (and wavelengths) as rows
        data = data.T.reset_index()

        # drop NA's
        # 2023-11-13 - the NAs are due to differing runtimes. At this point in the program the data is row-wise labels, columnwise mins/features, thus NA patterns are column-based, not all samples will have the same number of columns

        data = data.pipe(self.check_for_na)
        data = data.pipe(
            self.select_included_classes,
            min_num_samples=min_class_size,
            target_col=target_col,
        )
        data = data.pipe(self.enlarge_dataset, **enlarge_kwargs)

        logger.info(
            f"constructing feature matrix 'x' by removing {[target_col]+drop_cols} from input frame.."
        )

        x = data.drop([target_col] + drop_cols, axis=1)

        logger.info(
            f"constructing label matrix 'y' by selecting {target_col} from input frame.."
        )
        y = data.loc[:, target_col]

        return x, y

    def check_for_na(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        check_for_na drop observation columns if NA is detected

        Models such as PCA cannot handle NA values, and require that all samples have
        the same shape, therefore we need to drop any observation columns with an NA
        value.

        :param data: wide dataframe with labels and observations as columns, samples as rows.
        :type data: pd.DataFrame
        :return: wide dataframe without any NA value elements.
        :rtype: pd.DataFrame
        """

        logger.info("checking if df has any NA:")

        na_count = data.isna().sum().sum()

        if na_count > 0:
            logger.info(
                f"input df has {na_count} NA values, which are incompatible with modeling. All columns with NA will be dropped.."
            )

            df_shape = data.shape

            data = data.dropna(axis=1)

            new_df_shape = data.shape

            logger.info(
                f"Through dropping of columns containing NA, shape has gone from {df_shape} to {new_df_shape}"
            )
        return data

    def enlarge_dataset(self, data: pd.DataFrame, multiplier: int = 1) -> pd.DataFrame:
        """
        enlarge_dataset duplicate the dataset to inflate number of samples

        Small datasets lead to overfitting, or in the case of XGBoost, fail to grow trees.

        One brute method of increasing dataset size is to simply duplicate the samples.

        :param data: wide dataframe with labels and observations as columns, samples as rows.
        :type data: pd.DataFrame
        :param multiplier: multiplier by which to increase the size of the dataframe, defaults to 1
        :type multiplier: int, optional
        :raises ValueError: must be int or float
        :return: dataframe enlarged in accordance with the multiplier
        :rtype: pd.DataFrame
        """

        if not isinstance(multiplier, (int, float)):
            raise ValueError(
                f"multiplier must be int or float, got {type(multiplier)}.."
            )

        if multiplier > 1:
            logger.info(
                f"Enlarging dataset through duplication by a factor of {multiplier}.."
            )

            for i in range(1, multiplier):
                data = pd.concat([data, data])
                logger.info(
                    f" Iteration {i} resulted in a dataset of size: {data.shape}.."
                )

        return data

    def select_included_classes(
        self, data: pd.DataFrame, target_col: str, min_num_samples: int = 6
    ) -> pd.DataFrame:
        """
        select_included_classes filter classes of size below defined threshold

        XGBoost requires that classes contain enough samples to avoid overfitting.
        This function groups the input `data` by the `target_col` and eliminates any
        groups/classes that have less than `min_num_samples`

        :param data: wide dataframe with labels and observations as columns, samples as rows.
        :type data: pd.DataFrame
        :param target_col: label of column that will be the classification target/grouper
        :type target_col: str
        :param min_num_samples: minimum required number of samples in a class, defaults to 6
        :type min_num_samples: int, optional
        :return: dataframe with classes equal to or greater than `min_num_samples`
        :rtype: pd.DataFrame
        """

        logger.info(
            f"Selecting classes in {data[target_col]} that have size greater or equal to {min_num_samples}.."
        )

        classes = data[target_col].value_counts().loc[lambda x: x >= min_num_samples]

        class_labels = classes.index

        logger.info(f"classes selected as follows:\n{classes}")

        data = data.loc[lambda df: df[target_col].isin(class_labels)]

        return data


class MyData(dataextract.DataExtractor, data_pipeline.DataPipeline, ModelPrepper):
    def __init__(self, db_path: str) -> tuple:
        dataextract.DataExtractor.__init__(self, db_path=db_path)

        self.raw_data_ = None

        self.detection_ = ("raw",)
        self.exclude_ids_ = tuple(definitions.EXCLUDEIDS.values())
        self.wavelengths_ = (256,)
        self.color_ = ("red",)

    def model_pipeline(
        self, process_frame_kwargs: dict = dict(), model_prep_kwargs: dict = dict()
    ) -> tuple:
        """
        model_pipeline A pipeline running from the database to transformed feature and
        label frame/series respectively.

        Intended to be used to extract, clean and transform data prior to submission to
        Sklearn pipeline.

        It includes:
        1. retrieval of the raw data with hardcoded selection values
        2. signal processing to standardize the sample signals and remove noise
        3. transform and select the dataset ready for modeling, including splitting the
        target labels and the feature matrix.

        :param process_frame_kwargs: kwargs for `DataPipeline.process_frame`, defaults to dict()
        :type process_frame_kwargs: dict, optional
        :param model_prep_kwargs: kwargs for `ModelPrepper.prep_for_model`, defaults to dict()
        :type model_prep_kwargs: dict, optional
        :return: returns a tuple of (x, y) where x is the feature matrix and y is the
        classification target labels
        :rtype: tuple
        """

        self.create_subset_table(
            detection=self.detection_,
            exclude_ids=self.exclude_ids_,
            exclude_samplecodes=self.exclude_samplecodes_,
            wavelengths=self.wavelengths_,
            color=self.color_,
        )

        self.raw_data_ = self.get_tbl_as_df()

        self.pro_data_ = self.raw_data_.pipe(self.process_frame, **process_frame_kwargs)

        self.x, self.y = self.pro_data_.pipe(self.prep_for_model, **model_prep_kwargs)

        return self.x, self.y


class TestData:
    def __init__(self):
        self.getdata()
        self.prep_for_model()

    def getdata(self):
        # get the iris dataset and prep it to resemble my dataset
        irisbunch = datasets.load_iris()
        self.data = pd.DataFrame(data=irisbunch.data, columns=irisbunch.feature_names)
        self.data["target"] = irisbunch.target
        self.data.target = self.data.target.replace(
            {
                0: irisbunch.target_names[0],
                1: irisbunch.target_names[1],
                2: irisbunch.target_names[2],
            }
        )

    def prep_for_model(self):
        self.x = self.data.drop("target", axis=1)
        self.y = self.data.target
