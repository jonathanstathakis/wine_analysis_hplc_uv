import pandas as pd


def masker(df: pd.DataFrame) -> pd.DataFrame:
    """
    a bool df mask containing the 'avantor' column sample runs, in contrast to the HALO which was used for all other samples.
    """
    df = df[
        (df["uv_filenames"] != "")
        & (df["acq_method"].str.contains("AVANTOR"))
        & ~(df["id"].str.contains("uracil"))
        & ~(df["id"].str.contains("coffee"))
        & ~(df["id"].str.contains("lor"))
    ]

    return df
