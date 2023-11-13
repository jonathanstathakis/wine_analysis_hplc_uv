import logging

logger = logging.getLogger(__name__)

from sklearn import datasets

from wine_analysis_hplc_uv import definitions
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import data_pipeline
from wine_analysis_hplc_uv.notebooks.xgboost_modeling import dataextract


import pandas as pd


class MyData(data_pipeline.DataPipeline):
    def __init__(self, db_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load the data into the class object and prepare it for modeling, splitting the labels and features
        """
        self.db_path_ = db_path
        logger.info("Loading dataset..")

    def get_dset(self):
        """
        Get the dataset through the DataPipeline class as a sql query, return the transposed form with samples as rows and labels + observations as columns, with a reset index
        """
        append = True

        de = dataextract.DataExtractor(self.db_path_)

        de.create_subset_table(
            detection=("raw",),
            exclude_ids=tuple(definitions.EXCLUDEIDS.values()),
            exclude_samplecodes=("98",),
            wavelengths=256,
            color=("red",),
        )

        self.raw_data_ = de.get_tbl_as_df()
        return self.raw_data_

    def prep_for_model(
        self,
        target_col: str,
        label_cols: str | list,
        drop_cols=str | list,
        enlarge_kwargs: dict = dict(),
    ):
        """
        Remove NAs,
        """

        self.data = self.processed_df.T.reset_index()

        # drop NA's
        # 2023-11-13 - the NAs are due to differing runtimes. At this point in the program the data is row-wise labels, columnwise mins/features, thus NA patterns are column-based, not all samples will have the same number of columns

        logger.info("checking if df has any NA:")

        na_count = self.data.isna().sum().sum()

        if na_count > 0:
            logger.info(
                f"input df has {na_count} NA values, which are incompatible with modeling. All columns with NA will be dropped.."
            )

            df_shape = self.data.shape

            self.data = self.data.dropna(axis=1)

            new_df_shape = self.data.shape

            logger.info(
                f"Through dropping of columns containing NA, shape has gone from {df_shape} to {new_df_shape}"
            )

        self.data = self.select_included_classes()

        self.data = self.enlarge_dataset(**enlarge_kwargs)

        logger.info(
            f"constructing feature matrix 'x' by removing {[self.target_col]+self.drop_cols} from input frame.."
        )
        self.x = self.data.drop([self.target_col] + self.drop_cols, axis=1)

        logger.info(
            f"constructing label matrix 'y' by selecting {self.target_col} from input frame.."
        )
        self.y = self.data.loc[:, self.target_col]

        return self.x, self.y

    def enlarge_dataset(self, multiplier: int = 1):
        """
        Artifically increasing the size of the dataset to see if that affects model as of
        2023-11-06 13:15:22 I am getting the same predictions every run
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
                self.data = pd.concat([self.data, self.data])
                logger.info(
                    f" Iteration {i} resulted in a dataset of size: {self.data.shape}.."
                )

        return self.data

    def select_included_classes(self, min_num_samples: int = 6):
        """
        Subset the dataset size based on how many samples in a given class

        Note: selects for pinot noir and shiraz varietals only, both with 11 members currently 2023-11-06.
        """

        logger.info(
            f"Selecting classes in {self.target_col} that have size greater or equal to {min_num_samples}.."
        )

        classes = (
            self.data[self.target_col]
            .value_counts()
            .loc[lambda x: x >= min_num_samples]
        )

        class_labels = classes.index

        logger.info(f"classes selected as follows:\n{classes}")

        self.data = self.data.loc[lambda df: df[self.target_col].isin(class_labels)]

        return self.data


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
