# NCAA Revenue Allocation Analysis

Regression analysis of athletic revenue, scholarship investment, and student-athlete
graduation outcomes across 30 NCAA Division I athletic programs.

## Data

- **Financial data**: US Department of Education [Equity in Athletics Data Analysis
  (EADA)](https://ope.ed.gov/athletics/) survey, AY2023-24, institution-level file
  (`data/raw/EADA_2023-24/EADA_2024.xlsx`). Covers total athletic revenue, total
  athletic expense, and athletic student aid (scholarships) for every Title IV
  postsecondary institution with an athletics program.
- **Outcome data**: NCAA [Graduation Success Rate (GSR)
  database](https://web3.ncaa.org/aprsearch/gsrsearch), 2018 entering cohort (the
  most recent cohort with a completed 6-year GSR window). GSR is the NCAA's own
  academic-outcome metric and, unlike the Federal Graduation Rate, does not count a
  student-athlete against a school if they transfer out in good academic standing.
  Federal Graduation Rate (FGR) is pulled alongside GSR as a robustness check.
- **Sample**: A stratified random sample (seed 42) of 30 D1 programs — 10 FBS, 10
  FCS, 10 D1-without-football — drawn from the full population of 356 D1 programs in
  the EADA universe. Stratifying across the three D1 subdivisions was a deliberate
  choice to get real variation in program size (the sample spans $13.7M to $221M in
  total athletic revenue) rather than a sample dominated by a single tier.

## Why GSR lags the financial year

GSR is a 6-year rolling outcome measured from a single entering class (the "cohort
year"), not an annual figure — the 2018 cohort's GSR captures where those athletes
stood as of 2024. It structurally cannot be as current as the AY2023-24 financial
data. This is a real constraint of the GSR methodology, not a data-quality issue in
this analysis, and it's worth being able to explain in exactly those terms.

## Method

`scripts/build_dataset.py` merges the two sources on institution name and computes
derived variables (log revenue, student-aid share of revenue, enrollment in
thousands, D1-subdivision dummies). `scripts/analysis.do` runs the actual regression
in Stata (`StataNow/SE 19.5`, batch mode) and writes `results/analysis_log.log`.

Four models, each building on the last:
1. GSR on ln(revenue) alone
2. + scholarship investment as a share of revenue
3. + D1-subdivision controls (FCS, no-football) and enrollment
4. Same as (3), swapping in Federal Graduation Rate as the outcome, as a robustness
   check

## Findings

- Raw athletic revenue has **no significant relationship** with GSR on its own
  (Model 1, p = 0.23). A bigger athletic budget by itself doesn't predict better
  academic outcomes.
- Once scholarship investment (student aid as a share of total revenue) enters the
  model, **both** ln(revenue) and the aid share become significant predictors of GSR
  (Model 2, p = 0.014 and p = 0.021, R² = 0.23). Revenue and total scholarship
  dollars are highly correlated (r = 0.79, p < 0.001) — bigger programs spend more
  on aid in absolute terms — but it's the *share* of revenue actually reinvested in
  student aid, not program size, that's doing the work once separated out.
- Programs **without football** post GSRs about 5.5 points higher than otherwise
  comparable FBS/FCS programs, controlling for revenue and scholarship investment
  (Model 3, p = 0.028) — consistent with non-football D1 athletics skewing toward
  smaller rosters and sports with typically stronger baseline academic outcomes.
- The ln(revenue) relationship holds, more strongly, when Federal Graduation Rate
  replaces GSR as the outcome (Model 4, p = 0.002) — a real robustness check, not
  just restating Model 3.
- Enrollment size and FCS status (vs. the FBS baseline) are not significant
  predictors in any specification here.

**Bottom line**: athletic revenue's relationship to student outcomes isn't simple or
direct — it runs through what a program actually does with the money (scholarship
reinvestment), not through budget size alone, and the specific sports a program
sponsors matters as much as its finances.

## Reproducing this

```bash
python3 scripts/build_dataset.py                 # rebuild the merged CSV
stata-se -b do scripts/analysis.do                # rerun the regressions
```

Requires Stata (SE or higher) on PATH, or invoke the full binary path directly
(`/Applications/StataNow/StataSE.app/Contents/MacOS/stata-se`).
