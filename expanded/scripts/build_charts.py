"""
Generate the two static charts embedded in the interview packet, from the
real master_panel.csv data (no synthetic numbers). Matches the regression
models in analysis.py -- chart 1 visualizes Model 7.football, chart 2
visualizes Model 3 (per-sport win% ~ ln(revenue)).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

BLUE = "#2a78d6"
GRAY = "#8a8a86"
TEXT = "#1a1a19"
MUTED = "#52514e"
GRID = "#e3e2dd"

plt.rcParams.update({
    "font.family": "Helvetica",
    "text.color": TEXT,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

df = pd.read_csv("data/processed/master_panel.csv")
df["ln_revenue"] = np.log(df["revenue_total"].replace(0, np.nan))
df["win_pct"] = df["wins"] / (df["wins"] + df["losses"] + df["ties"].fillna(0))

# --- Chart 1: football aid share vs GSR, with fitted line ---
fb = df[df["sport"] == "football"].dropna(subset=["gsr", "aid_share_of_revenue"])

fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=200)
ax.scatter(fb["aid_share_of_revenue"] * 100, fb["gsr"], s=34, color=BLUE, alpha=0.75,
           edgecolors="white", linewidths=0.6, zorder=3)

m = smf.ols("gsr ~ aid_share_of_revenue", data=fb).fit()
xs = np.linspace(fb["aid_share_of_revenue"].min(), fb["aid_share_of_revenue"].max(), 50)
ys = m.params["Intercept"] + m.params["aid_share_of_revenue"] * xs
ax.plot(xs * 100, ys, color=TEXT, linewidth=2, zorder=2)

ax.set_xlabel("Scholarship/aid share of athletics revenue (%)", fontsize=9.5)
ax.set_ylabel("Graduation Success Rate", fontsize=9.5)
ax.set_title("Football: aid share predicts GSR (p = 0.029)", fontsize=11.5, color=TEXT,
             fontweight="bold", loc="left", pad=10)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.tick_params(labelsize=8.5)
fig.tight_layout()
fig.savefig("packet/chart_aid_share_gsr.png", facecolor="white")
plt.close(fig)

# --- Chart 2: revenue-to-wins coefficient by sport ---
sports = ["football", "basketball", "volleyball", "soccer"]
rows = []
for sport in sports:
    s = df[df["sport"] == sport].dropna(subset=["win_pct", "ln_revenue"])
    mm = smf.ols("win_pct ~ ln_revenue", data=s).fit(cov_type="HC1")
    coef = mm.params["ln_revenue"]
    ci = mm.conf_int().loc["ln_revenue"]
    pval = mm.pvalues["ln_revenue"]
    rows.append({"sport": sport.capitalize(), "coef": coef, "lo": ci[0], "hi": ci[1],
                 "sig": pval < 0.05, "p": pval})
coefs = pd.DataFrame(rows).iloc[::-1].reset_index(drop=True)

fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=200)
y = np.arange(len(coefs))
colors = [BLUE if s else GRAY for s in coefs["sig"]]
ax.hlines(y, coefs["lo"], coefs["hi"], color=colors, linewidth=3, zorder=2)
ax.scatter(coefs["coef"], y, s=60, color=colors, zorder=3, edgecolors="white", linewidths=0.8)
ax.axvline(0, color=GRID, linewidth=1, zorder=1)

for i, row in coefs.iterrows():
    pstr = "p < 0.001" if row["p"] < 0.001 else f"p = {row['p']:.3f}"
    label = pstr + ("  (sig.)" if row["sig"] else "  (n.s.)")
    ax.text(row["hi"] + 0.012, i, label, va="center", fontsize=8.3, color=MUTED)

ax.set_yticks(y)
ax.set_yticklabels(coefs["sport"], fontsize=9.5)
ax.set_xlabel("Effect of ln(revenue) on win percentage (regression coefficient, 95% CI)", fontsize=9)
ax.set_title("Revenue predicts wins, but strength varies by sport", fontsize=11.5, color=TEXT,
             fontweight="bold", loc="left", pad=10)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_xlim(-0.08, 0.26)
ax.tick_params(labelsize=8.5)
fig.tight_layout()
fig.savefig("packet/chart_revenue_wins_by_sport.png", facecolor="white")
plt.close(fig)

print("Wrote packet/chart_aid_share_gsr.png and packet/chart_revenue_wins_by_sport.png")
