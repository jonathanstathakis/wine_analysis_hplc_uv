import pandas as pd
from wine_analysis_hplc_uv.df_methods import df_cleaning_methods
from wine_analysis_hplc_uv.etl.build_library.generic import Exporter
import re
import logging

logger = logging.getLogger(__name__)


class ChMCleaner(Exporter):
    def clean_ch_m(self, df) -> pd.DataFrame:
        """
        driver function for cleaning chemstation metadata table to enable joins with sample_tracker table
        """

        self.df = (
            df.pipe(df_cleaning_methods.df_string_cleaner)
            .pipe(rename_ch_m_collabels)
            .pipe(format_acq_date)
            .pipe(replace_116_sigurd)
            .pipe(ch_m_samplecode_cleaner)
            # .pipe(chemstation_metadata_drop_unwanted_runs)
        )

        return self.df


def rename_ch_m_collabels(df):
    """ """
    original_names = ["notebook", "date", "method", "Injection Volume"]
    new_names = ["samplecode", "acq_date", "acq_method", "inj_vol"]

    rename_dict = dict(zip(original_names, new_names))
    df = df.rename(rename_dict, axis=1)
    assert not df.columns.isin(original_names).any()
    assert df.columns.isin(new_names).any()
    return df


def ch_m_samplecode_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. create 'join_samplecode' col based on 'id'
    2. rename 'id' col 'exp_id' to preserve that connection
    3.
    """
    assert isinstance(df, pd.DataFrame)
    df["join_samplecode"] = df["samplecode"]
    df = df.rename({"samplecode": "ch_samplecode"}, axis=1)

    logger.debug(msg="cleaning chemstation run id's")
    df["join_samplecode"] = four_to_two_digit(series=df["join_samplecode"])
    df = replace_samplecodes(df)
    assert "2021-debortoli-cabernet-merlot_avantor" not in df["join_samplecode"]
    assert isinstance(df, pd.DataFrame)
    return df


def replace_116_sigurd(df: pd.DataFrame):
    """
    Modifies sigurd chenin blanc samplecode from 116 to sigurdcb, as there was a doubleup.
    """

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # check that there are two 116s in the column
    # if not, might not need this function
    assert "samplecode" in df.columns, df.columns
    assert "sigurdcb" not in df["samplecode"].tolist()

    try:
        num_116 = df["samplecode"].value_counts()["116"]

        assert num_116 == 2, df["samplecode"].value_counts()["116"]
        replacement_str = "sigurdcb"

        # mask for the row containing 'sigurd' in the description col
        sigurd_mask = df["desc"].str.contains("sigurd", na=False)
        # make sure there is at least 1 True value
        assert sigurd_mask.isin([True]).any()
        # make the value replacement
        df.loc[sigurd_mask, "samplecode"] = replacement_str
        # make sure there is now only 1 '116'
        assert (
            df[df["samplecode"] == "116"].shape[0] == 1
        ), f"{df[df['samplecode'] == '116']}"
        # make sure there is 1 'sigurdcb'
        assert (
            df[df["samplecode"] == replacement_str].shape[0] == 1
        ), f"{df[df['samplecode'] == replacement_str]}"

    except AssertionError:
        logging.warning(
            f"Only {num_116} 116 samplecode in library. Skipped renaming to sigurdcb process"
        )

    return df


def four_to_two_digit(series: pd.Series) -> pd.DataFrame:
    pattern = get_four_digit_code_regex()

    def extract_middle_digits(x):
        match = pattern.match(x)
        return match.group(1) if match else x

    series = series.astype(str).apply(extract_middle_digits)
    return series


def get_four_digit_code_regex():
    return re.compile(
        "^0(\d{2})[12]$"
    )  # The pattern matches 4-digit strings starting with '0' and ending with '1'


def replace_samplecodes(series: pd.Series) -> pd.DataFrame:
    """
    Replaces the id of a number of runs with their 2 digit id's
    as stated in the sample tracker.
    """

    replace_dict = {
        "mt-diff-bannock-pn": "mt-diff-bannockburn-pn",
        "2021-debortoli-cabernet-merlot_avantor": "72",
        "stoney-rise-pn_02-21": "73",
        "crawford-cab_02-21": "74",
        "hey-malbec_02-21": "75",
        "koerner-nellucio-02-21": "76",
        "z3": "00",
    }

    series = series.replace(to_replace=replace_dict)
    return series


def format_acq_date(df):
    """
     Chemstation parsed timestamps are in the following format: 18-May-23, 21:39:50, or 'dd-Mth-yy, hh:mm:ss' Desire them to be in 'yyyy-mm-dd hh:mm:ss'.

     format codes can be found here: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

     According to the 1989 C standard:

    'dd-Mth-yy, hh:mm:ss' = '%d-%b-%y, %H:%M:%S'
    'yyyy-mm-dd hh:mm:ss' = '%Y-%m-%d, %H:%M:%S'

    """
    df["acq_date"] = pd.to_datetime(
        df["acq_date"], format="%d-%b-%y, %H:%M:%S", errors="raise"
    )
    df["acq_date"] = df["acq_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


# def chemstation_metadata_drop_unwanted_runs(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     legacy code. As the data library is now static, i manually excluded these files from the set.
#     """
#     df = df[
#         ~(df["join_samplecode"] == "coffee")
#         & ~(df["join_samplecode"] == "lor-ristretto")
#         & ~(df["join_samplecode"] == "espresso")
#         & ~(df["join_samplecode"] == "lor-ristretto_column-check")
#         & ~(df["join_samplecode"] == "nc0")
#         & ~(df["exp_id"].isna())
#     ]

#     return df
