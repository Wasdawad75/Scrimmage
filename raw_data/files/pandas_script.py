import pandas as pd

df = pd.read_csv("raw_data/files/Career_Stats_Rushing.csv")

print(df.columns.tolist())
print(df.shape)
print(df.head())
print(df.dtypes)
print(df.isnull().sum())
print(df[df["Player Id"] == "fredevans/2513736"][["Year", "Games Played"]])


df_basic = pd.read_csv("raw_data/files/Basic_Stats.csv")
print(df_basic.columns.tolist())
print(df_basic.head())