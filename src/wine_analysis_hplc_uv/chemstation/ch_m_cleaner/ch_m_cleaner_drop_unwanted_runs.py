def chemstation_metadata_drop_unwanted_runs(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        ~(df["new_id"] == "coffee")
        & ~(df["new_id"] == "lor-ristretto")
        & ~(df["new_id"] == "espresso")
        & ~(df["new_id"] == "lor-ristretto_column-check")
        & ~(df["new_id"] == "nc0")
        & ~(df["exp_id"].isna())
    ]

    return df
