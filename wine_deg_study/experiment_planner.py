import datetime
import os
import sys

import numpy as np
import pandas as pd

from wine_analysis_hplc_uv.etl.build_library.google_sheets_api.google_sheets_api import (
    post_df_as_sheet_values,
    post_new_sheet,
)

sys.path.append("/Users/jonathan/wine_analysis_hplc_uv/")
print(sys.path)


def google_sheets_write_info():
    # path_to_certs = os.path.join(os.getcwd(), '..')
    path_to_certs = os.path.join(os.getcwd(), "agilette/modules/credientals_tokens/")
    sheet_id = "15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY"

    return path_to_certs, sheet_id


def sample_code_gen(exp=[], num_wines=int, num_rep=int):
    exp = pd.DataFrame(exp, columns=["exp"])
    wine = pd.DataFrame(
        [str(wine + 1).zfill(2) for wine in range(0, num_wines)], columns=["wine"]
    )
    reps = pd.DataFrame(
        [str(rep + 1).zfill(2) for rep in range(0, num_rep)], columns=["rep"]
    )

    exp["key"] = 1
    reps["key"] = 1
    wine["key"] = 1

    result = pd.merge(exp, reps, on="key")
    result = pd.merge(result, wine, on="key")[["exp", "rep", "wine"]]

    result["code"] = result["exp"] + result["wine"] + result["rep"]
    return result


def schedule_df_genner():
    start_date = datetime.date(2023, 4, 18)
    end_date = start_date + datetime.timedelta(days=14)
    print(end_date)
    dates = pd.date_range(start_date, end_date, freq="D")
    times = pd.date_range("04:00", "17:00", freq="H").time
    schedule_df = pd.DataFrame(np.repeat(dates, len(times)), columns=["date"])
    schedule_df["weekday"] = schedule_df["date"].dt.day_name()
    schedule_df["time"] = np.tile(times, len(dates))
    schedule_df["datetime"] = pd.to_datetime(
        schedule_df["date"].astype(str) + " " + schedule_df["time"].astype(str)
    )
    # schedule_df = schedule_df.drop(['date', 'time'], axis=1)
    schedule_df = schedule_df.drop("datetime", axis=1)

    return schedule_df


def main():
    sample_code_gen(["a", "n", "e"], 3, 7)

    schedule_df_genner()

    creds, sheet_id = google_sheets_write_info()

    new_sheet_name = "freezer_exp_schedule"
    schedule_out_range = f"{new_sheet_name}!A1:C1000"

    # post_new_sheet(sheet_id, new_sheet_name, creds)

    # schedule table
    # post_df_as_sheet_values(df = schedule_df, spreadsheet_id = sheet_id, range = schedule_out_range, creds_parent_path = creds)
    # sample codes
    # post_df_as_sheet_values(df = codes, spreadsheet_id = sheet_id, range = code_out_range, creds_parent_path =creds)

    df = pd.read_csv(os.path.join(os.getcwd(), "schedule.csv"))
    df = df[~(df["experimenter"].isna())]
    post_new_sheet(sheet_id, "freezer_exp_schedule1", creds)
    schedule_out_range = "freezer_exp_schedule1!A1:E1000"

    post_df_as_sheet_values(
        df=df,
        spreadsheet_id=sheet_id,
        range=schedule_out_range,
        creds_parent_path=creds,
    )

    # print(df.head())


main()
