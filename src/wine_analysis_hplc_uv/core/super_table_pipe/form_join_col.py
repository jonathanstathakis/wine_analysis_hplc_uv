"""

"""


def form_join_col(df):
    print("forming join col..\n")
    df["join_key"] = df["vintage"].astype(str) + " " + df["name"]
    return df


def main():
    return None


if __name__ == "__main__":
    main()
