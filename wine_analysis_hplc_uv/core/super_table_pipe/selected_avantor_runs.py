import pandas as pd

from ...devtools import project_settings


def selected_avantor_runs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects runs to be included in study dataset.
    """
    print(
        f"Filtering for selected underivatized avantor column runs. df starts with {df.shape[0]} runs"
    )

    df = df[(df["acq_date"] > "2023-01-01")]

    print(f"after filtering for 2023 runs, {df.shape[0]} runs remaining\n")

    print(
        f"Filtering for avantor method runs, {df.shape[0]} runs remaining. Removing:\n{df[~(df['acq_method'].str.contains('avantor'))]}\n"
    )

    df = df[df["acq_method"].str.contains("avantor")]

    sequences_to_drop = (
        list(
            df.groupby("sequence_name")
            .filter(lambda x: len(x) == 1)
            .groupby("sequence_name")
            .groups.keys()
        )
        + df[df["sequence_name"].str.contains("dups")]["sequence_name"]
        .unique()
        .tolist()
        + df[df["sequence_name"].str.contains("repeat")]["sequence_name"]
        .unique()
        .tolist()
        + df[df["sequence_name"].str.contains("44min")]["sequence_name"]
        .unique()
        .tolist()
        + df[df["sequence_name"].str.contains("acetone")]["sequence_name"]
        .unique()
        .tolist()
    )

    sequence_drop_mask = df["sequence_name"].isin(sequences_to_drop) == False
    print(
        f"Filtering out 'dups', 'repeat', '44min', 'acetone' runs, {df.shape[0]} runs remaining. Removing:\n\n{df[~sequence_drop_mask].groupby('sequence_name').size()}"
    )

    df = df[sequence_drop_mask]

    return df
