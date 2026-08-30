# NCAA Revenue, NIL, and Outcomes: Expanded Multi-Sport Analysis

An expansion of the original 30-school NCAA Revenue Allocation Analysis (kept
intact in the repo root — this is a second, larger analysis, not a replacement).
Covers the full population of Power 4 + Pac-12 remnant conferences plus 13
non-P5 schools known for prominent basketball/other-sport programs, across
football, basketball, volleyball, and (for schools without football) men's
soccer as an equalizer sport.

## Sample: 83 schools, 249 school-sport rows

- **Big Ten (18), SEC (16), Big 12 (16), ACC (18 incl. Notre Dame), Pac-12
  remnant (2)** — real 2024-25 conference membership (post-realignment).
  "Power 5" is used loosely: the historical Pac-12 dissolved to 2 schools
  (Oregon State, Washington State) by 2024-25; the announced "new Pac-12"
  (adding Boise State, Colorado State, Fresno State, San Diego State, Utah
  State, Gonzaga for basketball) doesn't take effect until the 2026-27
  season, after this project's data window, so those additions are **not**
  included as Pac-12 here.
- **Notre Dame** is a full ACC member for basketball/volleyball but an FBS
  independent for football — its football revenue, wins, and GSR are real
  and included, just not attributed to the ACC.
- **13 non-P5 schools**: the 10 non-football Big East members (Butler,
  Creighton, DePaul, Georgetown, Marquette, Providence, Seton Hall, St.
  John's, Villanova, Xavier), Gonzaga and Saint Mary's (WCC), and Denver
  (Summit League). **Real correction made during data collection**: Butler,
  Georgetown, and Villanova actually sponsor real FCS football (Pioneer
  League, Patriot League, and CAA respectively) — confirmed against the
  actual EADA data, not assumed from Big East membership. Their real
  football numbers are used instead of the soccer equalizer. The remaining
  10 schools have zero football program (confirmed against EADA), and use
  men's soccer as the equalizer sport — verified as sponsored by all 10
  before locking in the design.

## Data sources

- **Financial data (revenue, expense, participants, by sport)**: US Dept of
  Education EADA survey, **survey year 2024 (= AY2023-24)** — this is the
  most recent year actually published; despite the Oct 15, 2025 reporting
  deadline for AY2024-25 having passed, that data is not yet in the EADA
  database as of this analysis (2026-08-30). Pulled live via the site's
  `customData/filesByFilter` API (same technique as the original 30-school
  project), one POST per sport code (football/basketball/volleyball/soccer),
  covering all ~2,037 Title IV institutions, then filtered to the 83-school
  list. Real per-sport men's/women's revenue and expense figures, not just
  total athletics.
- **Scholarship/aid investment share (institution-level)**: same EADA
  survey year, pulled via the site's "ALL DATA COMBINED" category
  (`categories: [22]`, distinct from the per-sport pull above), the one
  path that actually includes athletically related student aid. Confirmed
  against the raw federal EADA data dictionary that aid is genuinely never
  broken out by individual sport, unlike revenue/expense/participants,
  which are, so this is a school-level control (aid ÷ total athletics
  revenue), the same variable and construction the original 30-school
  project used.
- **Win-loss records**: real 2025-26 season data (2025 for football/soccer,
  2025-26 for basketball/volleyball — whichever season is most recently
  complete), pulled from NCAA's own official stats site
  (stats.ncaa.org, "Match W-L Pctg." team report) and Wikipedia/Warren Nolan
  conference standings pages. **This creates a real ~2-year offset between
  the financial year (AY2023-24) and the wins year (2025-26)**, the same
  kind of structural lag the original project already documents for GSR —
  disclosed here rather than hidden.
- **Graduation Success Rate (GSR/FGR)**: NCAA's official GSR search tool
  (web3.ncaa.org/aprsearch/gsrsearch), **2018 entering cohort** (most recent
  complete 6-year window, same as the original project). Unlike the
  original project's one-by-one school search, this tool supports
  conference+sport combined queries — pulled real GSR for the **entire
  population** of all 83 schools across their relevant sports (not a
  sample), a stronger design than originally planned.
- **NIL valuation**: On3's live NIL 100 (individual player valuations,
  dated 2026-08-30), summed by school for football and basketball only.
  **These are estimates of roster/brand value, not verified spend, and
  On3 doesn't track NIL for volleyball or soccer at all.** See "The NIL
  problem" below — this is the weakest link in the dataset by design, not
  by oversight.

## The NIL problem (read before trusting the NIL results)

There is no official, public record of what a school or its NIL collective
actually spends on a roster — nothing like EADA exists for NIL. On3's NIL
100 is a real, current, dated product, but it only ranks the top 100
individual players nationally. Investigated and rejected during this
project:
- A "team NIL rankings" list that circulated with real-looking dollar
  totals for ~40 schools turned out, on verification, to be from
  **November 2023** — using it would have silently fabricated recency.
  Discarded.
- An untracked, uncommitted file (`../.discarded_unverified/gsr_expanded/`,
  moved aside not deleted) was found in the original repo containing GSR
  numbers for ~94 schools including conferences never discussed for this
  project. No record of it in any session log or git history — it has the
  signature of fabricated placeholder data, not real hand-collected
  numbers. Not used for anything in this analysis.

Given that, the NIL variable here is **"sum of On3 NIL 100 valuations, for
schools that have at least one player in the current national top 100"** —
real and dated, but only meaningfully populated for ~40 of 83 schools in
football and ~27 in basketball. A school with `nil100_sum = 0` means **"not
in the national top 100,"** not **"spends nothing on NIL."** All NIL models
in this analysis explicitly restrict to schools that do have NIL-100
presence, to avoid treating that absence as a real zero.

## Method

`scripts/build_sport_dataset.py` filters the 4 raw EADA sport-code pulls
down to the 83-school list. `scripts/build_aid_share.py` extracts the
institution-level scholarship/aid share from the separate EADA "all data
combined" pull. `scripts/build_master_dataset.py` merges in wins, GSR, NIL,
and aid share (each source uses different name conventions —
EADA official names, common/short names for wins, On3 slugs for NIL — all
reconciled by hand-verified mapping, not fuzzy matching, given the schools
list is small enough to check exactly). `scripts/analysis.py` runs the
regressions in Python/statsmodels (robust HC1 SEs), deliberately not Stata,
consistent with the Labor Market project's precedent of not repeating the
same tool across resume projects.

## Findings (real, not decided in advance)

**Revenue predicts wins, but the strength varies a lot by sport.**
Pooled across all sports (win% ~ ln(revenue), sport fixed effects, P5
dummy, n=246): revenue is a significant positive predictor (coef 0.062,
p<0.001). Broken out by sport: **basketball** (coef 0.150, p<0.001) and
**volleyball** (coef 0.059, p=0.005) both show real, significant
revenue-to-wins relationships; **football** is only marginal (p=0.075);
**soccer** shows no relationship (p=0.554, but n=10, underpowered).

**Revenue's relationship with graduation rate is the surprising one, and
it's sport-specific, until scholarship share enters the model.** Pooled
(GSR ~ ln(revenue), sport FE, P5 dummy, n=247), the revenue coefficient is
negative and only marginally significant (p=0.087). Broken out by sport,
**football is the real story on its own**: more football revenue
significantly predicts a *lower* GSR (coef -2.67, p=0.004), the opposite
direction from what "more resources helps academics" would suggest.

**Adding scholarship/aid investment share resolves it, and replicates the
original 30-school project's core finding at this larger scale.** EADA
does not report athletically related student aid broken out by individual
sport (confirmed against the raw federal data dictionary — revenue,
expense, and participants are all reported per sport, aid is not, only as
an institution-wide men's/women's/coed total), so this is a school-level
control rather than a per-sport one, same as the original project's own
variable. Once it's added (GSR ~ ln(revenue) + aid share + sport FE + P5,
n=247), **aid share is a significant positive predictor of GSR** (coef
44.12, p=0.009, R² rises to 0.311). Broken out by sport, the effect is
concentrated in **football**: aid share is significant there on its own
(coef 52.83, p=0.029), and — this is the real finding — **once aid share
is in the model, football's revenue coefficient stops being significant**
(p=0.328, down from p=0.004 without it). Raw football revenue's apparent
negative effect on GSR was standing in for scholarship reinvestment share
all along: it's not that more football money hurts academics, it's that
big-revenue programs which *don't* reinvest proportionally in aid have
worse outcomes, exactly the original project's core insight, now shown to
hold specifically within football. Basketball, volleyball, and soccer show
no significant aid-share effect on their own (basketball p=0.132,
volleyball p=0.865, soccer p=0.289, the last two likely underpowered).

**NIL, restricted to the schools that actually have national-tier NIL
valuations**: NIL sum significantly predicts win% (coef 0.071, p=0.005,
n=70) but not GSR (p=0.584). And unsurprisingly, revenue strongly predicts
whether a school has any NIL-100 presence at all (p<0.001) — NIL
visibility concentrates at the schools that already have the most money,
it isn't an independent variable spreading opportunity more evenly.

Full regression output: `results/analysis_log.txt`. A 2-page interview
packet summarizing schools, findings, and methodology is at
`packet/NCAA_Expanded_Analysis_Packet.{docx,pdf}`.

## What's not in this analysis

- Women's basketball is not included; "basketball" here means men's only,
  a deliberate scope call matching where NIL/revenue conversation actually
  concentrates, documented here rather than left silent.
- NIL for volleyball/soccer doesn't exist in any public source and isn't
  included as a variable at all (not even a caveated one).
