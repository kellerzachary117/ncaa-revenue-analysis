"""
Regression analysis on the expanded multi-sport panel (83 schools x football/
basketball/volleyball/soccer-equalizer = 249 school-sport rows).

Questions:
1. Does more revenue/expense predict more wins, by sport?
2. Does revenue (and, where available, NIL) predict graduation rate (GSR), by sport?
3. Pooled model: win_pct ~ ln(revenue) + sport fixed effects + P5 dummy
4. NIL-specific models (football/basketball only, since NIL data only exists there,
   and only for schools that had a player in the current On3 NIL 100 -- most of the
   sample has nil100_sum = 0, meaning "not in the national top 100", not "zero spend")
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

df = pd.read_csv("data/processed/master_panel.csv")

df["win_pct"] = df["wins"] / (df["wins"] + df["losses"] + df["ties"].fillna(0))
df["ln_revenue"] = np.log(df["revenue_total"].replace(0, np.nan))
df["ln_expense"] = np.log(df["expense_total"].replace(0, np.nan))
df["p5"] = (df["subdivision"] == "P5").astype(int)
df["has_nil_data"] = (df["nil100_sum_valuation_estimate"] > 0).astype(int)

log = open("results/analysis_log.txt", "w")
def report(title, res):
    log.write(f"\n{'='*70}\n{title}\n{'='*70}\n")
    log.write(str(res.summary()))
    log.write("\n")
    print(f"\n{'='*70}\n{title}\n{'='*70}")
    print(res.summary())

# --- Model 1: pooled win_pct ~ ln(revenue) + sport FE + P5 ---
sub = df.dropna(subset=["win_pct", "ln_revenue"])
m1 = smf.ols("win_pct ~ ln_revenue + C(sport) + p5", data=sub).fit(cov_type="HC1")
report("Model 1: Win% ~ ln(Revenue) + Sport FE + P5 dummy (pooled, all sports)", m1)

# --- Model 2: pooled GSR ~ ln(revenue) + sport FE + P5 ---
sub2 = df.dropna(subset=["gsr", "ln_revenue"])
m2 = smf.ols("gsr ~ ln_revenue + C(sport) + p5", data=sub2).fit(cov_type="HC1")
report("Model 2: GSR ~ ln(Revenue) + Sport FE + P5 dummy (pooled, all sports)", m2)

# --- Model 3: per-sport win_pct ~ ln(revenue) ---
for sport in ["football", "basketball", "volleyball", "soccer"]:
    s = df[df["sport"] == sport].dropna(subset=["win_pct", "ln_revenue"])
    if len(s) < 8:
        continue
    m = smf.ols("win_pct ~ ln_revenue", data=s).fit(cov_type="HC1")
    report(f"Model 3.{sport}: Win% ~ ln(Revenue), {sport} only (n={len(s)})", m)

# --- Model 4: per-sport GSR ~ ln(revenue) ---
for sport in ["football", "basketball", "volleyball", "soccer"]:
    s = df[df["sport"] == sport].dropna(subset=["gsr", "ln_revenue"])
    if len(s) < 8:
        continue
    m = smf.ols("gsr ~ ln_revenue", data=s).fit(cov_type="HC1")
    report(f"Model 4.{sport}: GSR ~ ln(Revenue), {sport} only (n={len(s)})", m)

# --- Model 5: NIL-100 sum vs GSR/wins, football + basketball only, restricted to
# schools that actually have a nonzero NIL100 figure (avoids treating "not in the
# national top 100" as "zero NIL spend") ---
nil_sub = df[(df["sport"].isin(["football", "basketball"])) & (df["has_nil_data"] == 1)].copy()
nil_sub["ln_nil"] = np.log(nil_sub["nil100_sum_valuation_estimate"])
m5a = smf.ols("gsr ~ ln_nil + C(sport)", data=nil_sub.dropna(subset=["gsr", "ln_nil"])).fit(cov_type="HC1")
report(f"Model 5a: GSR ~ ln(NIL100 sum) + sport FE, football+basketball schools WITH NIL-100 presence (n={len(nil_sub.dropna(subset=['gsr','ln_nil']))})", m5a)

m5b = smf.ols("win_pct ~ ln_nil + C(sport)", data=nil_sub.dropna(subset=["win_pct", "ln_nil"])).fit(cov_type="HC1")
report(f"Model 5b: Win% ~ ln(NIL100 sum) + sport FE, football+basketball schools WITH NIL-100 presence (n={len(nil_sub.dropna(subset=['win_pct','ln_nil']))})", m5b)

# --- Model 6: does revenue predict NIL-100 presence at all? (sanity check on what
# "being in the national NIL conversation" actually correlates with) ---
fb_bb = df[df["sport"].isin(["football", "basketball"])].dropna(subset=["ln_revenue"])
m6 = smf.ols("has_nil_data ~ ln_revenue + C(sport)", data=fb_bb).fit(cov_type="HC1")
report(f"Model 6: P(in NIL-100) ~ ln(Revenue) + sport FE (n={len(fb_bb)})", m6)

log.close()
print("\nWrote results/analysis_log.txt")
