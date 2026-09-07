from pathlib import Path

import pandas as pd

data_dir = Path(__file__).resolve().parent
basic = pd.read_csv(data_dir / "Basic_Stats.csv")
passing = pd.read_csv(data_dir / "Career_Stats_Passing.csv")

# your turn: merge these two on "Player Id"
merged_qb = pd.merge(basic, passing, on="Player Id", how="inner")



columns_to_drop = [
	"Name_y",
	"Position_x",
	"Position_y",
	"High School",
	"High School Location",
	"Number",
	"Current Status",
]
merged_qb = merged_qb.drop(columns=columns_to_drop)
merged_qb["position"] = "QB"

passing_stat_columns = [
	"Passes Attempted",
	"Passes Completed",
	"Completion Percentage",
	"Pass Attempts Per Game",
	"Passing Yards",
	"Passing Yards Per Attempt",
	"Passing Yards Per Game",
	"TD Passes",
	"Percentage of TDs per Attempts",
	"Ints",
	"Int Rate",
	"Longest Pass",
	"Passes Longer than 20 Yards",
	"Passes Longer than 40 Yards",
	"Sacks",
	"Sacked Yards Lost",
	"Passer Rating",
]
merged_qb[passing_stat_columns] = (
	merged_qb[passing_stat_columns]
	.replace("--", pd.NA)
	.apply(pd.to_numeric, errors="coerce")
)

merged_qb = merged_qb.dropna(subset=["Passing Yards", "Passes Attempted"], how="all")

merged_qb = merged_qb[merged_qb["Passes Attempted"] >= 15]

merged_qb.to_csv(data_dir / "merged_qbs.csv", index=False)

print(merged_qb.shape) 
print(merged_qb.columns.tolist())
print(f"Rows after filtering: {merged_qb.shape}")
# think about: what happens to columns that exist in both files (like Name, Position)?
# pandas' merge() has a `suffixes` parameter for exactly this collision
