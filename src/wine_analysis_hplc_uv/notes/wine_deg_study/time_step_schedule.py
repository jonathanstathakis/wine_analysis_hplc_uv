import pandas as pd

datetime_range = pd.date_range("2023-04-12 19:00", "2023-04-13 04:00", freq="2.2H")

df = pd.DataFrame(datetime_range)

df["datetime+1"] = df["datetime_range"]
print(df)
