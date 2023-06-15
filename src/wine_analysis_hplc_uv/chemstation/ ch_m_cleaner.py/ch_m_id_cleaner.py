import pandas as pd


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


def four_digit_id_to_two_digit(series: pd.Series) -> pd.DataFrame:
    series = series.astype(str).apply(lambda x: x[1:3] if len(x) == 4 else x)
    return series


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
