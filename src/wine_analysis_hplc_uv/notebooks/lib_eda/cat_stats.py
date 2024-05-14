import pandas as pd


def num_unique_wines_by_detect_by_type(in_df, type_order):
    # count of unique wines by type
    df = in_df.copy()

    out_df = (
        df.groupby(["type"])[["wine"]]
        .nunique()
        .reset_index()
        # .sort_values(["wine", 'type'], ascending=[False, False])
        .rename({"wine": "count"}, axis=1)
        # .set_index('type')
    )

    out_df["type"] = pd.Categorical(out_df["type"], categories=type_order, ordered=True)
    out_df = out_df.sort_values("type", ascending=True)
    out_df = out_df.set_index("type")
    out_df.index = out_df.index.astype(str)
    return out_df


def num_unique_wines_by_detect_by_country(in_df):
    # count of unique wines by country
    detection = in_df["detection"].iloc[0]
    out_df = (
        in_df.groupby(["country"])[["wine"]]
        .nunique()
        .reset_index()
        .sort_values(["wine", "country"], ascending=[False, True])
        .rename({"wine": "count"}, axis=1)
    )
    out_df["detection"] = detection
    return out_df


def num_unique_wines_by_detect_by_vintage(in_df):
    # count of unique wines by vintage
    in_df["vintage"] = in_df["vintage"].astype(int)

    out_df = (
        in_df.groupby(["detection", "vintage"])[["wine"]]
        .nunique()
        .reset_index(["vintage", "detection"])
        .sort_values(["vintage", "wine", "detection"], ascending=[False, False, False])
    )
    out_df = out_df.rename({"wine": "count"}, axis=1)
    out_df["count"] = out_df["count"].astype(int)

    return out_df
