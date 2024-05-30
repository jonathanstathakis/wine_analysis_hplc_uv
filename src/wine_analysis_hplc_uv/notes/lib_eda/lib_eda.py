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


def get_test_df():
    # 2020 noname shiraz has 1 raw, 1 cuprac
    # 2021 alphabet chard has 1 cuprac
    # 2018 zwelt riesling has 1 raw
    # 2000 blewitt springs moscato has 2 raw

    test_df = pd.DataFrame(
        dict(
            wine=[
                "2020 noname shiraz",
                "2020 noname shiraz",
                "2020 noname shiraz",
                "2021 alphabet chard",
                "2018 zwelt riesling",
                "2000 blewitt springs",
                "2000 blewitt springs",
            ],
            detection=[
                "cuprac",
                "raw",
                "raw",
                "cuprac",
                "raw",
                "raw",
                "raw",
            ],
        )
    )
    return test_df


def samples_without_repeats(in_df):
    # count of samples without repeats
    unrepeated_samples_df = (
        in_df.groupby(["detection", "wine"])
        .size()
        .to_frame(name="n")
        .loc[lambda x: x["n"] == 1]
    )

    return unrepeated_samples_df


def samples_with_repeats(in_df):
    # total count of inviduals in data set who are repetitions
    inter_df = in_df

    repeats = (
        inter_df.set_index(["detection", "wine"])
        .index.value_counts()
        .loc[lambda s: s > 1]
        .to_frame(name="n")
    )
    return repeats


# TODO:convert the other description functions into this format further use down the track then aggregate their values into the summary tabl


#######################################################################################


def summary_table(df):
    samples_with_repeats_df = samples_with_repeats(df)

    unrepeated_samples_df = samples_without_repeats(df)

    # num samples per detect cat
    num_samples_by_detect = df.groupby("detection").size().rename("tot_samples")

    # individual wines
    ind_df = df.loc[:, ["detection", "wine"]].drop_duplicates()

    # number of individual wines per detect method
    num_ind_by_detect = ind_df.groupby(["detection"]).size().rename("n_ind_samples")

    # num samples with repeats
    num_samples_w_repeat = (
        samples_with_repeats_df.groupby("detection")
        .size()
        .rename("num_samples_w_repeat")
    )

    # number of wines without repeats
    num_samples_no_repeat = (
        unrepeated_samples_df.groupby("detection")
        .size()
        .rename("num_samples_no_repeat")
    )

    # total number of repeats per detect cat
    num_repeated_per_detect = (
        samples_with_repeats_df.groupby("detection")
        .sum()
        .rename({"n": "tot_num_repeats"}, axis=1)
    )

    # to enter into the summary table need to be series with index detect, values 'n'
    # formed by .groupby(['detection'].size().rename("measure"))

    summary_df = pd.concat(
        [
            num_samples_by_detect,
            num_ind_by_detect,
            num_samples_w_repeat,
            num_samples_no_repeat,
            num_repeated_per_detect,
        ],
        axis=1,
    ).rename_axis("statistic", axis="columns")

    summary_pivot_df = (
        summary_df.T.reset_index()
        .melt(id_vars="statistic")
        .pivot_table(
            columns="detection",
            index="statistic",
            values="value",
            margins=True,
            margins_name="total",
            aggfunc=sum,
            sort=False,
        )
        .drop("total")  # total row is meaningless in this context
    )

    return summary_pivot_df


#######################################################################################


#######################################################################################


def detection_intersection(df):
    # find the intersection of detection methods,
    # i.e. samples that were detected under both configs

    both_detect_df = (
        df.groupby("wine")
        .filter(lambda x: x["detection"].nunique() >= 2)
        .reset_index(drop=True)
        .groupby(["wine", "detection"])
        .size()
        .reset_index(name="n")
        .pivot_table(
            index="wine",
            columns="detection",
            values="n",
            margins=True,
            margins_name="total",
            aggfunc=sum,
        )
        .assign(is_total=lambda x: x.index == "total")
        .sort_values(["total"], ascending=False)
        .sort_values(["is_total"])
        .drop("is_total", axis=1)
        .reindex()
    )
    return both_detect_df


def main():
    import os

    df = (
        pd.read_excel(
            os.path.join(os.path.dirname(__file__), "..", "df.xlsx"), dtype=object
        )
        .rename({"vintage_ct": "vintage"}, axis=1)
        .assign(wine=lambda x: x["vintage"] + " " + x["name_ct"])
        .loc[lambda x: ~x["wine"].isna()]
    )
    assert not df.empty

    summary_table(df)


if __name__ == "__main__":
    main()
