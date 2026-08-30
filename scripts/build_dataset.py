"""
Merge the EADA 2023-24 financial sample (30 D1 schools, stratified across
FBS/FCS/D1-no-football) with NCAA GSR 2018-cohort outcome data, and write
a clean analysis file for Stata.

Sources:
- data/raw/EADA_2023-24/EADA_2024.xlsx (US Dept of Education, Equity in
  Athletics Data Analysis, AY 2023-24 survey, institution-level)
- data/raw/gsr_2018_cohort.csv (NCAA Graduation Success Rate database,
  web3.ncaa.org/aprsearch/gsrsearch, 2018 entering cohort - most recent
  GSR cohort available; GSR is a 6-year rolling rate so it necessarily
  lags the financial-year data)
"""
import pandas as pd

sample = pd.read_csv("data/raw/sample_30_schools.csv")
gsr = pd.read_csv("data/raw/gsr_2018_cohort.csv")

df = sample.merge(gsr, on="institution_name", how="left")
assert df["gsr"].notna().all(), "unmatched schools remain"

df["fbs"] = (df["classification_name"] == "NCAA Division I-FBS").astype(int)
df["fcs"] = (df["classification_name"] == "NCAA Division I-FCS").astype(int)
df["no_football"] = (df["classification_name"] == "NCAA Division I without football").astype(int)

df["revenue_millions"] = df["GRND_TOTAL_REVENUE"] / 1_000_000
df["expense_millions"] = df["GRND_TOTAL_EXPENSE"] / 1_000_000
df["student_aid_millions"] = df["STUDENTAID_TOTAL"] / 1_000_000
df["aid_share_of_revenue"] = df["STUDENTAID_TOTAL"] / df["GRND_TOTAL_REVENUE"]
df["enrollment_thousands"] = df["EFTotalCount"] / 1_000

out = df[[
    "unitid", "institution_name", "state_cd", "classification_name",
    "fbs", "fcs", "no_football",
    "enrollment_thousands",
    "revenue_millions", "expense_millions",
    "student_aid_millions", "aid_share_of_revenue",
    "gsr", "fgr",
]].rename(columns={"state_cd": "state"})

out = out.sort_values("revenue_millions", ascending=False).reset_index(drop=True)
out.to_csv("data/processed/ncaa_revenue_analysis.csv", index=False)
print(out.to_string(index=False))
print(f"\nWrote {len(out)} rows to data/processed/ncaa_revenue_analysis.csv")
