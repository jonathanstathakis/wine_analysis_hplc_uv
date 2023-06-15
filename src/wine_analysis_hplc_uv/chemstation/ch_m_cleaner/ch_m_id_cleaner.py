import pandas as pd
import re


def ch_m_id_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. create 'new_id' col based on 'id'
    2. rename 'id' col 'exp_id' to preserve that connection
    3.
    """
    df["new_id"] = df["id"]
    df = df.rename({"id": "exp_id"}, axis=1)

    print("cleaning chemstation run id's")
    df = four_digit_id_to_two_digit(series=df["new_id"])
    df = string_id_to_digit(df)
    return df


def get_four_digit_code_regex():
    return re.compile(
        "^0(\d{2})1$"
    )  # The pattern matches 4-digit strings starting with '0' and ending with '1'


def four_digit_id_to_two_digit(series: pd.Series) -> pd.DataFrame:
    pattern = get_four_digit_code_regex()

    def extract_middle_digits(x):
        match = pattern.match(x)
        return match.group(1) if match else x

    series = series.astype(str).apply(extract_middle_digits)
    return series


# def four_digit_id_to_two_digit(series: pd.Series) -> pd.DataFrame:
#     series = series.astype(str).apply(lambda x: x[1:3] if len(x) == 4 else x)
#     return series


def string_id_to_digit(series: pd.Series) -> pd.DataFrame:
    """
    Replaces the id of a number of runs with their 2 digit id's
    as stated in the sample tracker.
    """

    replace_dict = {
        "2021-debortoli-cabernet-merlot_avantor|debertoli_cs": "72",
        "stoney-rise-pn_02-21": "73",
        "crawford-cab_02-21": "74",
        "hey-malbec_02-21": "75",
        "koerner-nellucio-02-21": "76",
        "z3": "00",
    }

    series = series.replace(to_replace=replace_dict)
    return series
