"""
Filter the four EADA AY2023-24 sport-code pulls (football, basketball,
volleyball, soccer -- covering all 2037 Title IV institutions) down to the
83-school Power 5 + non-P5 sample, and reshape into one row per
school/sport with revenue, expense, and participant counts.

Sources: data/raw/eada_2024_{football,basketball,volleyball,soccer}.csv
(US Dept of Education EADA, survey year 2024 = AY2023-24, pulled live via
the site's customData/filesByFilter endpoint, one POST per sport code).
"""
import pandas as pd

SPORTS = ["football", "basketball", "volleyball", "soccer"]

schools = pd.read_csv("data/raw/school_list.csv")
schools["institution_name"] = schools["institution_name"].str.strip()

rows = []
unmatched = {s: [] for s in SPORTS}

for sport in SPORTS:
    df = pd.read_csv(f"data/raw/eada_2024_{sport}.csv")
    df["Institution Name"] = df["Institution Name"].str.strip()
    for _, school in schools.iterrows():
        name = school["institution_name"]
        match = df[df["Institution Name"] == name]
        if match.empty:
            unmatched[sport].append(name)
            continue
        r = match.iloc[0]
        rows.append({
            "institution_name": name,
            "conference": school["conference"],
            "subdivision": school["subdivision"],
            "has_football": school["has_football"],
            "sport": sport,
            "men_participants": r["# Participants Men's Team"],
            "women_participants": r["# Participants Women's Team"],
            "revenue_men": r["Revenues Men's Team"],
            "revenue_women": r["Revenues Women's Team"],
            "expense_men": r["Expenses Men's Team"],
            "expense_women": r["Expenses Women's Team"],
        })

out = pd.DataFrame(rows)
out.to_csv("data/processed/sport_financials.csv", index=False)
print(f"Wrote {len(out)} school-sport rows to data/processed/sport_financials.csv")

for sport, names in unmatched.items():
    if names:
        print(f"\nUnmatched in {sport} ({len(names)}):")
        for n in names:
            print(f"  - {n}")
