"""
categories:
'size_ct',
'vintage',
'name_ct',
'locale',
'country',
'region', 
'subregion',
'appellation',
'producer',
'type',
'varietal',
"""

import pandas as pd
import logging
import numpy as np


def calc_prop(series, tot_size):
    return series / tot_size * 100


def count_subpop_detection(in_df):
    # Counts of rows by detection type
    out_df = in_df.groupby("detection").size()
    out_df = out_df.reset_index(name="n")
    out_df = out_df.set_index("detection")
    out_df["prop"] = 100.00
    mindex = pd.MultiIndex.from_product([out_df.index, ["subpop_size"]])
    out_df.index = mindex
    out_df = out_df
    return out_df


def count_individuals(in_df):
    # num individual samples in data set
    out_df = in_df.groupby(["detection"])["wine"].nunique()
    out_df = out_df.reset_index(name="n")
    out_df = out_df.set_index("detection")
    out_df["prop"] = np.round(out_df["n"] / in_df.shape[0], 2)
    out_df["prop"] = calc_prop(out_df["n"], in_df.shape[0])
    mindex = pd.MultiIndex.from_product([out_df.index, ["count_individs"]])
    out_df.index = mindex

    return out_df


def count_unrepeated_samples(in_df):
    # count of samples without repeats
    # get the count of repetitions of each sample
    vcount_df = (
        in_df.groupby(["detection"])["wine"]
        .value_counts()
        .reset_index()
        .rename({"count": "n"}, axis=1)
    )
    # filter out any who has a repetition greater than 1, i.e. 1 occurance
    unique_df = vcount_df[vcount_df["n"] == 1]
    # get the count of rows remaining after filtering

    out_df = (
        unique_df.groupby(["detection"])["wine"]
        .count()
        .reset_index(name="n")
        .set_index("detection")
    )
    out_df["prop"] = calc_prop(out_df["n"], in_df.shape[0])
    mindex = pd.MultiIndex.from_product([out_df.index, ["count_unrep"]])
    out_df.index = mindex
    return out_df


def count_repeated_samples(in_df):
    # count of individuals who have at least one repetition
    vcount_df = (
        in_df.groupby(["detection"])["wine"]
        .value_counts()
        .reset_index()
        .rename({"count": "n"}, axis=1)
    )
    dup_df = vcount_df[vcount_df["n"] > 1]
    out_df = (
        dup_df.groupby(["detection"])["wine"]
        .count()
        .reset_index(name="n")
        .set_index("detection")
    )
    out_df["prop"] = calc_prop(out_df["n"], in_df.shape[0])
    mindex = pd.MultiIndex.from_product([out_df.index, ["count_reps"]])
    out_df.index = mindex
    return out_df


def size_tot_repeats(in_df):
    # total count of inviduals in data set who are repetitions
    out_df = in_df.groupby(["detection", "wine"]).size().reset_index(name="n")
    out_df = out_df[out_df["n"] > 1]
    out_df = out_df.groupby("detection")["n"].sum().reset_index()
    out_df["prop"] = calc_prop(out_df["n"], in_df.shape[0])
    out_df = out_df.set_index("detection")
    mindex = pd.MultiIndex.from_product([out_df.index, ["size_repeats"]])
    out_df.index = mindex
    return out_df


#######################################################################################


def summary_table(df):
    n = count_subpop_detection(df)
    count_individuals_df = count_individuals(df)
    count_unrepeated_samples_df = count_unrepeated_samples(df)
    count_repeated_samples_df = count_repeated_samples(df)
    size_repeated_df = size_tot_repeats(df)

    summary_df = pd.concat(
        [
            n,
            count_individuals_df,
            count_repeated_samples_df,
            count_unrepeated_samples_df,
            size_repeated_df,
        ],
        axis=0,
    )

    return summary_df


#######################################################################################


def add_descriptor_columns(df):
    out_df = df.copy()
    out_df["cumsum"] = out_df["count"].cumsum()
    out_df["prop"] = calc_prop(out_df["count"], out_df["count"].sum())
    out_df.loc["total"] = out_df.sum()
    out_df["cumsum_prop"] = out_df["prop"].cumsum()
    out_df["prop"] = out_df["prop"].apply(np.round, 2)
    out_df["cumsum_prop"] = out_df["cumsum_prop"].apply(np.round, 2)
    out_df["count"] = out_df["count"].astype(int)
    out_df["cumsum"] = out_df["cumsum"].apply(int)
    out_df["cumsum"] = out_df["cumsum"].astype(str)
    out_df.loc["total", "cumsum"] = out_df["cumsum"].iloc[-2]
    out_df.loc["total", "cumsum_prop"] = out_df["cumsum_prop"].iloc[-2]

    if "detection" in out_df.columns:
        out_df.loc["total", "detection"] = np.nan
    out_df = out_df.fillna("")
    return out_df


def show_barplot(df, **kwargs):
    return df["count"].plot.bar(**kwargs)


def num_unique_wines_by_detect_by_variety(in_df):
    # The counts of each varietal by detection
    detection = in_df["detection"].iloc[0]
    out_df = (
        in_df.groupby(["varietal"])["wine"]
        .nunique()
        .reset_index()
        .rename({"wine": "count"}, axis=1)
        .sort_values(["count"], ascending=[False])
        .set_index("varietal")
    )
    out_df["count"] = out_df["count"].astype(int)
    out_df["detection"] = detection
    out_df = add_descriptor_columns(out_df)
    return out_df


def num_unique_wines_by_detect_by_type(in_df):
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
    order = [
        "white - sparkling",
        "rosé - sparkling",
        "white",
        "orange",
        "rosé",
        "red",
        "white - sweet/dessert",
    ]
    out_df["type"] = pd.Categorical(out_df["type"], categories=order, ordered=True)
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
