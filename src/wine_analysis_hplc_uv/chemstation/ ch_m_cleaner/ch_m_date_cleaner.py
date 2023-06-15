import pandas as pd


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
