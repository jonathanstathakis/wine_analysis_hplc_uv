def chemstation_metadata_drop_unwanted_runs(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        ~(df["join_samplecode"] == "coffee")
        & ~(df["join_samplecode"] == "lor-ristretto")
        & ~(df["join_samplecode"] == "espresso")
        & ~(df["join_samplecode"] == "lor-ristretto_column-check")
        & ~(df["join_samplecode"] == "nc0")
        & ~(df["exp_id"].isna())
    ]

    return df
