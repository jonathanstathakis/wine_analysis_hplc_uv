from os import replace
import pandas as pd
import re
from wine_analysis_hplc_uv.chemstation import logger


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
    df = replace_116_sigurd(df)
    assert "2021-debortoli-cabernet-merlot_avantor" not in df["join_samplecode"]
    assert isinstance(df, pd.DataFrame)
    return df


def four_to_two_digit(series: pd.Series) -> pd.DataFrame:
    def get_four_digit_code_regex():
        return re.compile(
            "^0(\d{2})[12]$"
        )  # The pattern matches 4-digit strings starting with '0' and ending with '1'

    pattern = get_four_digit_code_regex()

    def extract_middle_digits(x):
        match = pattern.match(x)
        return match.group(1) if match else x

    series = series.astype(str).apply(extract_middle_digits)
    return series


def replace_116_sigurd(df: pd.DataFrame):
    """
    Modifies sigurd chenin blanc samplecode from 116 to sigurdcb, as there was a doubleup.
    """
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # check that there are two 116s in the column
    # if not, might not need this function
    assert df["join_samplecode"].value_counts()["116"] == 2

    replacement_str = "sigurdcb"

    # mask for the row containing 'sigurd' in the description col
    sigurd_mask = df["desc"].str.contains("sigurd", na=False)
    # make sure there is at least 1 True value
    assert sigurd_mask.isin([True]).any()
    # make the value replacement
    df.loc[sigurd_mask, "join_samplecode"] = replacement_str
    # make sure there is now only 1 '116'
    assert (
        df[df["join_samplecode"] == "116"].shape[0] == 1
    ), f"{df[df['join_samplecode'] == '116']}"
    # make sure there is 1 'sigurdcb'
    assert (
        df[df["join_samplecode"] == replacement_str].shape[0] == 1
    ), f"{df[df['join_samplecode'] == replacement_str]}"

    return df


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
