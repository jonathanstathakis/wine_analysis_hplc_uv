import pandas as pd
import numpy as np


def test_dataset():
    """
    Cuprac shiraz at 450nm with a random sampling of 5 observation points.

    154 has 1 observation more than the others, but its NaN.
    """

    def check_df(df):
        print(df.columns.get_level_values("vars"))
        assert False
        return df

    df = (
        pd.DataFrame(
            {
                ("154", "2020 leeuwin estate shiraz art series", "mins"): {
                    0: 17.6825,
                    1: 28.2825,
                    2: 31.7425,
                    3: 34.26916666666666,
                    4: 35.99583333333333,
                    5: np.nan,
                },
                ("154", "2020 leeuwin estate shiraz art series", "value"): {
                    0: 0,
                    1: 3.5185739398002625,
                    2: 4.017174243927002,
                    3: 3.0876919627189636,
                    4: 4.1618868708610535,
                    5: np.nan,
                },
                ("163", "2015 yangarra estate shiraz mclaren vale", "mins"): {
                    0: 17.684783333333332,
                    1: 28.284783333333333,
                    2: 31.744783333333334,
                    3: 34.27145,
                    4: 35.99811666666667,
                },
                ("163", "2015 yangarra estate shiraz mclaren vale", "value"): {
                    0: 4.745416343212128,
                    1: 6.816156208515167,
                    2: 0.3344714641571045,
                    3: 0.5525872111320496,
                    4: 0.521630048751831,
                },
                ("165", "2020 izway shiraz bruce", "mins"): {
                    0: 17.68166666666667,
                    1: 28.281666666666666,
                    2: 31.741666666666667,
                    3: 34.26833333333333,
                    4: 35.995,
                },
                ("165", "2020 izway shiraz bruce", "value"): {
                    0: 9.61562991142273,
                    1: 4.191294312477112,
                    2: 0.14627724885940552,
                    3: 0.0008419156074523926,
                    4: 0.05727261304855347,
                },
                ("176", "2021 john duval wines shiraz concilio", "mins"): {
                    0: 17.68645,
                    1: 28.28645,
                    2: 31.74645,
                    3: 34.27311666666667,
                    4: 35.99978333333333,
                },
                ("176", "2021 john duval wines shiraz concilio", "value"): {
                    0: 20.684920251369476,
                    1: 5.100332200527191,
                    2: 9.549513459205627,
                    3: 1.8068403005599976,
                    4: 1.110166311264038,
                },
                ("177", "2021 torbreck shiraz the struie", "mins"): {
                    0: 17.686666666666667,
                    1: 28.286666666666665,
                    2: 31.746666666666666,
                    3: 34.27333333333333,
                    4: 36.0,
                },
                ("177", "2021 torbreck shiraz the struie", "value"): {
                    0: 24.621665477752686,
                    1: 6.3974931836128235,
                    2: 8.841246366500854,
                    3: 1.0299012064933777,
                    4: 0.2767592668533325,
                },
                ("ca0301", "2021 chris ringland shiraz", "mins"): {
                    0: 17.680616666666666,
                    1: 28.280616666666667,
                    2: 31.740616666666668,
                    3: 34.26728333333333,
                    4: 35.99395,
                },
                ("ca0301", "2021 chris ringland shiraz", "value"): {
                    0: 4.944443702697754,
                    1: 4.77755069732666,
                    2: 0.40030479431152344,
                    3: 0.2757161855697632,
                    4: 0.2722740173339844,
                },
                ("torbreck-struie", "2021 torbreck shiraz the struie", "mins"): {
                    0: 17.685616666666668,
                    1: 28.285616666666666,
                    2: 31.745616666666667,
                    3: 34.272283333333334,
                    4: 35.99895,
                },
                ("torbreck-struie", "2021 torbreck shiraz the struie", "value"): {
                    0: 41.36265814304352,
                    1: 7.269956171512604,
                    2: 11.186964809894562,
                    3: 1.871950924396515,
                    4: 1.8909499049186707,
                },
            }
        )
        .rename_axis(["samplecode", "wine", "vars"], axis=1)
        .rename_axis("i", axis=0)
        .stack(["samplecode", "wine"])
        .reset_index()
        .set_index(["samplecode", "wine", "i"])
        .pipe(lambda df: df if print(df) else df)
        .assign(
            value=lambda df: df["value"].where(
                ~(df.index.get_level_values("i") == 0), 0
            )
        )  # set the first value to zero
        .assign(
            value=lambda df: df["value"].where(
                ~(df.index.get_level_values("i") == 4), 0
            )
        )  # set the last value to zero
        .assign(
            value=lambda df: df["value"].where(
                ~(df.index.get_level_values("i") == 3), df["value"].max()
            )
        )  # set the last to always be equal to the max, should ensure an always
        # positive baseline gradient
        .unstack(["samplecode", "wine"])
        .reorder_levels(["samplecode", "wine", "vars"], axis=1)
        .sort_index(axis=1)
        # .pipe(check_df)
    )
    return df


def good_mock_df():
    return (
        pd.DataFrame(
            {
                ("100", "2000 wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("100", "2000 wine", "value"): [5, 10, 50, 100, 50, 10],
                ("200", "1998 wine", "mins"): [0.1, 1.1, 2.1, 3.1, 4.1, np.nan],
                ("200", "1998 wine", "value"): [0, 100, 0, 25, 100, 10],
                ("201", "nv wine", "mins"): [0.01, 1.01, 2.01, 3.01, 4.01, 5.01],
                ("201", "nv wine", "value"): [0, 100, 0, 25, 100, 10],
                ("500", "wine", "mins"): [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                ("500", "wine", "value"): [0, 100, 0, 25, 100, 10],
            }
        )
        .rename_axis(["samplecode", "wine", "vars"], axis=1)
        .rename_axis("i", axis=0)
        # .pipe(lambda df: df if print(df) is None else df)
    )


def bad_mock_df():
    return (
        pd.DataFrame(
            {
                ("100", "2000 wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("100", "2000 wine", "value"): [5, 10, 50, 100, 50, 10],
                ("200", "1998 wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("200", "1998 wine", "value"): [0, 100, 0, 25, 100, 10],
                ("201", "nv wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("201", "nv wine", "value"): [0, 100, 0, 25, 100, 10],
                ("201", "wine", "mins"): [0, 1, 2, 3, 4, 5],
                ("201", "wine", "value"): [0, 100, 0, 25, 100, 10],
            }
        )
        .rename_axis(["samplecode", "wine", "vars"], axis=1)
        .rename_axis("i", axis=0)
        # .pipe(lambda df: df if print(df) is None else df)
    )
