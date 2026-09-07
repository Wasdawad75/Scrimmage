from pathlib import Path

import pandas as pd

data_dir = Path(__file__).resolve().parent
basic = pd.read_csv(data_dir / "Basic_Stats.csv")
rushing = pd.read_csv(data_dir / "Career_Stats_Rushing.csv")

# your turn: merge these two on "Player Id"
merged_rb = pd.merge(basic, rushing, on="Player Id", how="inner")



columns_to_drop = [
	"Name_y",
	"Position_x",
	"Position_y",
	"High School",
	"High School Location",
	"Number",
	"Current Status",
]
merged_rb = merged_rb.drop(columns=columns_to_drop)
merged_rb["position"] = "rb"

rushing_stat_columns = [
	"Rushing Attempts",
	"Rushing Attempts Per Game",
	"Rushing Yards",
    "Yards Per Carry",
	"Rushing Yards Per Game",
	"Rushing TDs",
	"Longest Rushing Run",
    "Rushing First Downs",
    "Percentage of Rushing First Downs",
    "Rushing More Than 20 Yards",
    "Rushing More Than 40 Yards",
    "Fumbles",
   
]
merged_rb[rushing_stat_columns] = (
	merged_rb[rushing_stat_columns]
	.replace("--", pd.NA)
	.apply(pd.to_numeric, errors="coerce")
)

merged_rb = merged_rb.dropna(subset=["Rushing Yards", "Rushing Attempts"], how="all")

merged_rb = merged_rb[merged_rb["Longest Rushing Run"] >= 10]

merged_rb.to_csv(data_dir / "merged_rbs.csv", index=False)

print(merged_rb.shape) 
print(merged_rb.columns.tolist())
print(f"Rows after filtering: {merged_rb.shape}")
# think about: what happens to columns that exist in both files (like Name, Position)?
# pandas' merge() has a `suffixes` parameter for exactly this collision