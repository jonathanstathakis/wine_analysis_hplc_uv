import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataPrepper:
    def transform_dataset(
        self,
        data: pd.DataFrame,
        target_col: str,
        drop_cols: str | list,
        enlarge_kwargs: dict = dict(),
        min_class_size: int | float = 1,
    ) -> tuple:
        """
        transform_dataset Take a dataframe and prepare it for model building

        Intended to be used on the output of `DataPipeline.process_frame`, take a tidy
        format frame with samples as columns and observations as rows and return
        a tuple of a feature matrix and label array (DataFrame and Series).

        :param data: tidy format dataframe with columns as samples and rows as observations
        :type data: pd.DataFrame
        :param target_col: The column of data containing the classification target labels
        :type target_col: str
        :param drop_cols: superfluous columns to be excluded from the output
        :type drop_cols: str | list
        :param enlarge_kwargs: kwargs for `DataPrepper.enlarge_dataset`, defaults to dict()
        :type enlarge_kwargs: dict, optional
        :param min_class_size: minimum class size required to be included in input dataset, defaults to 1
        :type min_class_size: int | float, optional
        :return: returns a tuple of (X, y) where targets are in y and features are in X
        :rtype: tuple (pd.DataFrame, pd.Series)
        """
        # orient frame with labels and observations as columns, samples (and wavelengths) as rows
        data = self.pro_data_.T.reset_index()

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

        X = data.drop([target_col] + drop_cols, axis=1)

        logger.info(
            f"constructing label matrix 'y' by selecting {target_col} from input frame.."
        )
        y = data.loc[:, target_col]

        return X, y

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
