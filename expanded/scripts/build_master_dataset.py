"""
Merge all raw sources into one school-sport panel:
- data/processed/sport_financials.csv (EADA AY2023-24 revenue/expense/participants, by sport)
- data/raw/wins_{football,basketball,volleyball,soccer}.csv (2025 season win-loss)
- data/raw/gsr_{football,basketball,volleyball,soccer}.csv (NCAA GSR 2018 cohort)
- data/raw/nil_estimates.csv (On3 NIL 100, football/basketball only, real but partial coverage)

Output: data/processed/master_panel.csv, one row per school-sport combination
actually used in the analysis (football OR soccer-as-equalizer, basketball, volleyball).
"""
import pandas as pd

schools = pd.read_csv("data/raw/school_list.csv")
fin = pd.read_csv("data/processed/sport_financials.csv")

wins = pd.concat([
    pd.read_csv("data/raw/wins_football.csv"),
    pd.read_csv("data/raw/wins_basketball.csv"),
    pd.read_csv("data/raw/wins_volleyball.csv"),
    pd.read_csv("data/raw/wins_soccer.csv"),
], ignore_index=True)

gsr = pd.concat([
    pd.read_csv("data/raw/gsr_football.csv"),
    pd.read_csv("data/raw/gsr_basketball.csv"),
    pd.read_csv("data/raw/gsr_volleyball.csv"),
    pd.read_csv("data/raw/gsr_soccer.csv"),
], ignore_index=True)

nil = pd.read_csv("data/raw/nil_estimates.csv")
aid = pd.read_csv("data/raw/aid_share.csv")

# On3 slug -> EADA institution_name mapping, only for schools that appear in nil_estimates.csv
SLUG_TO_NAME = {
    "miami-hurricanes": "University of Miami",
    "oregon-ducks": "University of Oregon",
    "ohio-state-buckeyes": "Ohio State University-Main Campus",
    "ole-miss-rebels": "University of Mississippi",
    "lsu-tigers": "Louisiana State University and Agricultural & Mechanical College",
    "washington-huskies": "University of Washington-Seattle Campus",
    "indiana-hoosiers": "Indiana University-Bloomington",
    "oklahoma-state-cowboys": "Oklahoma State University-Main Campus",
    "michigan-wolverines": "University of Michigan-Ann Arbor",
    "pittsburgh-panthers": "University of Pittsburgh-Pittsburgh Campus",
    "california-golden-bears": "University of California-Berkeley",
    "smu-mustangs": "Southern Methodist University",
    "texas-longhorns": "The University of Texas at Austin",
    "texas-am-aggies": "Texas A&M University-College Station",
    "notre-dame-fighting-irish": "University of Notre Dame",
    "auburn-tigers": "Auburn University",
    "tennessee-volunteers": "The University of Tennessee-Knoxville",
    "alabama-crimson-tide": "The University of Alabama",
    "utah-utes": "University of Utah",
    "vanderbilt-commodores": "Vanderbilt University",
    "byu-cougars": "Brigham Young University",
    "texas-tech-red-raiders": "Texas Tech University",
    "kentucky-wildcats": "University of Kentucky",
    "virginia-tech-hokies": "Virginia Polytechnic Institute and State University",
    "south-carolina-gamecocks": "University of South Carolina-Columbia",
    "kansas-state-wildcats": "Kansas State University",
    "nc-state-wolfpack": "North Carolina State University at Raleigh",
    "louisville-cardinals": "University of Louisville",
    "ucla-bruins": "University of California-Los Angeles",
    "missouri-tigers": "University of Missouri-Columbia",
    "arizona-wildcats": "University of Arizona",
    "baylor-bears": "Baylor University",
    "georgia-bulldogs": "University of Georgia",
    "nebraska-cornhuskers": "University of Nebraska-Lincoln",
    "virginia-cavaliers": "University of Virginia-Main Campus",
    "usc-trojans": "University of Southern California",
    "oklahoma-sooners": "University of Oklahoma-Norman Campus",
    "arizona-state-sun-devils": "Arizona State University Campus Immersion",
    "mississippi-state-bulldogs": "Mississippi State University",
    "tcu-horned-frogs": "Texas Christian University",
    "northwestern-wildcats": "Northwestern University",
    "syracuse-orange": "Syracuse University",
    "clemson-tigers": "Clemson University",
    "kansas-jayhawks": "University of Kansas",
    "florida-gators": "University of Florida",
    "st-johns-red-storm": "St. John's University-New York",
    "gonzaga-bulldogs": "Gonzaga University",
    "duke-blue-devils": "Duke University",
    "marquette-golden-eagles": "Marquette University",
    "north-carolina-tar-heels": "University of North Carolina at Chapel Hill",
    "providence-friars": "Providence College",
    "villanova-wildcats": "Villanova University",
    "illinois-fighting-illini": "University of Illinois Urbana-Champaign",
    "creighton-bluejays": "Creighton University",
    "houston-cougars": "University of Houston",
    "arkansas-razorbacks": "University of Arkansas",
    "west-virginia-mountaineers": "West Virginia University",
}
nil["institution_name"] = nil["school_slug"].map(SLUG_TO_NAME)
unmapped = nil[nil["institution_name"].isna()]["school_slug"].unique()
if len(unmapped):
    print("WARNING unmapped NIL slugs:", unmapped)
nil = nil.dropna(subset=["institution_name"])[["institution_name", "sport", "nil100_player_count", "nil100_sum_valuation_estimate"]]

# Build the school-sport key: for football-having schools, sport list = football/basketball/volleyball
# for no-football schools, sport list = basketball/volleyball/soccer (soccer stands in for football's slot)
rows = []
for _, s in schools.iterrows():
    name = s["institution_name"]
    sport_list = ["football", "basketball", "volleyball"] if s["has_football"] == 1 else ["basketball", "volleyball", "soccer"]
    for sport in sport_list:
        rows.append({"institution_name": name, "conference": s["conference"], "subdivision": s["subdivision"],
                      "has_football": s["has_football"], "sport": sport})
panel = pd.DataFrame(rows)

panel = panel.merge(fin, on=["institution_name", "sport"], how="left", suffixes=("", "_fin"))

# wins_*.csv use short/common names (conference-standings style); map EADA institution_name -> common name
EADA_TO_COMMON = {
    "University of Illinois Urbana-Champaign": "Illinois", "University of Iowa": "Iowa",
    "Indiana University-Bloomington": "Indiana", "University of Maryland-College Park": "Maryland",
    "University of Michigan-Ann Arbor": "Michigan", "Michigan State University": "Michigan State",
    "University of Minnesota-Twin Cities": "Minnesota", "University of Nebraska-Lincoln": "Nebraska",
    "Northwestern University": "Northwestern", "Ohio State University-Main Campus": "Ohio State",
    "University of Oregon": "Oregon", "Pennsylvania State University-Main Campus": "Penn State",
    "Purdue University-Main Campus": "Purdue", "Rutgers University-New Brunswick": "Rutgers",
    "University of California-Los Angeles": "UCLA", "University of Southern California": "USC",
    "University of Washington-Seattle Campus": "Washington", "University of Wisconsin-Madison": "Wisconsin",
    "The University of Alabama": "Alabama", "University of Arkansas": "Arkansas",
    "Auburn University": "Auburn", "University of Florida": "Florida", "University of Georgia": "Georgia",
    "University of Kentucky": "Kentucky",
    "Louisiana State University and Agricultural & Mechanical College": "LSU",
    "University of Missouri-Columbia": "Missouri", "Mississippi State University": "Mississippi State",
    "University of Mississippi": "Ole Miss", "University of Oklahoma-Norman Campus": "Oklahoma",
    "University of South Carolina-Columbia": "South Carolina", "The University of Tennessee-Knoxville": "Tennessee",
    "The University of Texas at Austin": "Texas", "Texas A&M University-College Station": "Texas A&M",
    "Vanderbilt University": "Vanderbilt", "University of Arizona": "Arizona",
    "Arizona State University Campus Immersion": "Arizona State", "Baylor University": "Baylor",
    "Brigham Young University": "BYU", "University of Central Florida": "UCF",
    "University of Cincinnati-Main Campus": "Cincinnati", "University of Colorado Boulder": "Colorado",
    "University of Houston": "Houston", "Iowa State University": "Iowa State",
    "University of Kansas": "Kansas", "Kansas State University": "Kansas State",
    "Oklahoma State University-Main Campus": "Oklahoma State", "Texas Christian University": "TCU",
    "Texas Tech University": "Texas Tech", "University of Utah": "Utah", "West Virginia University": "West Virginia",
    "Boston College": "Boston College", "University of California-Berkeley": "California",
    "Clemson University": "Clemson", "Duke University": "Duke", "Florida State University": "Florida State",
    "Georgia Institute of Technology-Main Campus": "Georgia Tech", "University of Louisville": "Louisville",
    "University of Miami": "Miami (FL)", "University of North Carolina at Chapel Hill": "North Carolina",
    "North Carolina State University at Raleigh": "North Carolina State",
    "University of Pittsburgh-Pittsburgh Campus": "Pittsburgh", "Southern Methodist University": "SMU",
    "Stanford University": "Stanford", "Syracuse University": "Syracuse",
    "Virginia Polytechnic Institute and State University": "Virginia Tech",
    "University of Virginia-Main Campus": "Virginia", "Wake Forest University": "Wake Forest",
    "University of Notre Dame": "Notre Dame", "Oregon State University": "Oregon State",
    "Washington State University": "Washington State", "Butler University": "Butler",
    "Creighton University": "Creighton", "DePaul University": "DePaul", "Georgetown University": "Georgetown",
    "Marquette University": "Marquette", "Providence College": "Providence",
    "Seton Hall University": "Seton Hall", "St. John's University-New York": "St. John's",
    "Villanova University": "Villanova", "Xavier University": "Xavier", "Gonzaga University": "Gonzaga",
    "Saint Mary's College of California": "Saint Mary's", "University of Denver": "Denver",
}
panel["common_name"] = panel["institution_name"].map(EADA_TO_COMMON)
unmapped_names = panel[panel["common_name"].isna()]["institution_name"].unique()
if len(unmapped_names):
    print("WARNING unmapped common names:", unmapped_names)
if "ties" not in wins.columns:
    wins["ties"] = 0
wins["ties"] = wins["ties"].fillna(0)
panel = panel.merge(wins[["institution", "sport", "wins", "losses", "ties"]], left_on=["common_name", "sport"],
                     right_on=["institution", "sport"], how="left").drop(columns=["institution", "common_name"])
panel = panel.merge(gsr[["institution_name", "sport", "cohort_year", "gsr", "fgr"]], on=["institution_name", "sport"], how="left")
panel = panel.merge(nil, on=["institution_name", "sport"], how="left")
panel["nil100_player_count"] = panel["nil100_player_count"].fillna(0)
panel["nil100_sum_valuation_estimate"] = panel["nil100_sum_valuation_estimate"].fillna(0)

# Institution-level scholarship/aid share: EADA does not break athletically related
# student aid out by individual sport (confirmed against the raw federal data
# dictionary -- it only reports men's/women's/coed totals), unlike revenue/expense/
# participants, which ARE reported per sport. So this is a school-level control,
# not a per-sport one, same as the original 30-school project's own variable.
panel = panel.merge(aid[["institution_name", "aid_share_of_revenue"]], on="institution_name", how="left")

# Combined revenue/expense (men's + women's, since football/men's basketball/men's soccer are
# effectively men's-only rows but volleyball is women's-only -- use whichever side has real data)
for col in ["revenue", "expense"]:
    panel[f"{col}_total"] = panel[[f"{col}_men", f"{col}_women"]].sum(axis=1, skipna=True)

panel.to_csv("data/processed/master_panel.csv", index=False)
print(f"Wrote {len(panel)} rows to data/processed/master_panel.csv")
print(f"Rows with real GSR: {panel['gsr'].notna().sum()} / {len(panel)}")
print(f"Rows with real wins: {panel['wins'].notna().sum()} / {len(panel)}")
print(f"Rows with real revenue: {panel['revenue_total'].notna().sum()} / {len(panel)}")
