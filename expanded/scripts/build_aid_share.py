"""
Extract institution-level scholarship/aid investment share from the EADA
"ALL DATA COMBINED" pull (categories: [22] in the site's customData API --
distinct from the per-sport pulls in eada_2024_{sport}.csv, which use a fixed
category that does not include student aid).

EADA does not report athletically related student aid broken out by
individual sport -- confirmed against the raw federal EADA data dictionary
(revenue, expense, and participants ARE reported per sport; aid is only
reported as a men's/women's/coed total for the whole athletic department).
So this is a school-level control, not a per-sport one, matching the
original 30-school project's own variable and construction.

Source: data/raw/eada_2024_all_data_combined.csv (same AY2023-24 survey
year, all ~2,037 Title IV institutions).
"""
import pandas as pd

df = pd.read_csv("data/raw/eada_2024_all_data_combined.csv")
schools = pd.read_csv("data/raw/school_list.csv")

cols = ["Institution Name", "Men's Team Athletic Student Aid",
        "Women's Team Athletic Student Aid", "Coed Team Athletic Student Aid",
        "Grand Total Revenue"]
sub = df[cols].copy()
sub["Institution Name"] = sub["Institution Name"].str.strip()
sub["total_aid"] = sub[cols[1]].fillna(0) + sub[cols[2]].fillna(0) + sub[cols[3]].fillna(0)
sub["aid_share_of_revenue"] = sub["total_aid"] / sub["Grand Total Revenue"]

merged = schools[["institution_name"]].merge(
    sub, left_on="institution_name", right_on="Institution Name", how="left")
unmatched = merged[merged["Institution Name"].isna()]["institution_name"].tolist()
if unmatched:
    print("WARNING unmatched schools:", unmatched)

out = merged[["institution_name", "total_aid", "Grand Total Revenue", "aid_share_of_revenue"]]
out.to_csv("data/raw/aid_share.csv", index=False)
print(f"Wrote {len(out)} rows to data/raw/aid_share.csv")
