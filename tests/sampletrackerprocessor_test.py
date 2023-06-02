from wine_analysis_hplc_uv.sampletracker import sampletrackerprocesser as st
import pandas as pd


def test_sampletracker_processor_init():
    sampletracker = st.SampleTracker()

    assert not sampletracker.df.empty, "sampletracker df is empty..\n"

    assert sampletracker.df.dtypes.apply(
        lambda x: isinstance(x, pd.StringDtype)
    ).all(), f"non-string column dtype detected:\n{sampletracker.df.dtypes}"

    # check that all the columns have at least some content

    # print(sampletracker.df.apply(lambda col: col.str.isalnum()).any())

    # opendate_is_alnum = sampletracker.df["open_date"].apply(
    #     lambda row: row.isalnum() if isinstance(row, str) else row
    # )
    # opendate_is_alnum = sampletracker.df["notes"].apply(lambda row: row.isspace())
    df = pd.DataFrame()

    df["emptycol"] = [""] * 5

    empties = ("", None)

    testresult = df["emptycol"].apply(lambda row: row in empties)

    print(df["emptycol"])
    print("Test result:")
    print(testresult.any())
    return None


def main():
    test_sampletracker_processor_init()


if __name__ == "__main__":
    main()
