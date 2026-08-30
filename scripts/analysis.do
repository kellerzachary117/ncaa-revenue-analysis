/*==============================================================================
NCAA Revenue Allocation Analysis
Data: 30 NCAA Division I athletic programs (10 FBS, 10 FCS, 10 D1 no-football),
      stratified random sample, seed 42, drawn from the full EADA AY2023-24
      universe of 356 D1 programs.
Sources: US Dept of Education EADA survey (revenue, expenses, student aid)
         merged with NCAA GSR 2018-cohort database (student-athlete outcomes).
==============================================================================*/

clear all
set more off
cd "~/Zeus/ncaa-revenue-analysis"

import delimited "data/processed/ncaa_revenue_analysis.csv", clear

label var revenue_millions "Total athletic revenue ($M)"
label var expense_millions "Total athletic expense ($M)"
label var student_aid_millions "Athletic student aid / scholarships ($M)"
label var aid_share_of_revenue "Student aid as share of total revenue"
label var enrollment_thousands "Total undergrad+grad enrollment (000s)"
label var gsr "Graduation Success Rate, 2018 cohort (%)"
label var fgr "Federal Graduation Rate, 2018 cohort (%)"

gen ln_revenue = ln(revenue_millions)
label var ln_revenue "Ln(athletic revenue, $M)"

log using "results/analysis_log.log", replace text

di as text _n "===== Descriptive statistics ====="
summarize revenue_millions expense_millions student_aid_millions ///
    aid_share_of_revenue gsr fgr enrollment_thousands, detail

di as text _n "===== Revenue by classification tier ====="
tabstat revenue_millions student_aid_millions gsr, by(classification_name) ///
    statistics(mean sd n) columns(statistics)

di as text _n "===== Correlation matrix ====="
pwcorr revenue_millions student_aid_millions aid_share_of_revenue gsr fgr, sig star(5)

* -----------------------------------------------------------------------------
* Model 1: Does raw athletic revenue predict student-athlete graduation
* outcomes, before controlling for anything else?
* -----------------------------------------------------------------------------
di as text _n "===== Model 1: GSR on ln(revenue) ====="
regress gsr ln_revenue, robust

* -----------------------------------------------------------------------------
* Model 2: Add scholarship investment (the resource that plausibly runs
* through to graduation, as opposed to revenue itself)
* -----------------------------------------------------------------------------
di as text _n "===== Model 2: GSR on ln(revenue) + aid share ====="
regress gsr ln_revenue aid_share_of_revenue, robust

* -----------------------------------------------------------------------------
* Model 3: Control for program tier (FBS is the omitted/base category) and
* institution size, since both are plausible confounds for both revenue and
* graduation outcomes.
* -----------------------------------------------------------------------------
di as text _n "===== Model 3: full model with tier + enrollment controls ====="
regress gsr ln_revenue aid_share_of_revenue fcs no_football enrollment_thousands, robust

* -----------------------------------------------------------------------------
* Model 4: Same specification, Federal Graduation Rate as the outcome
* instead of GSR, as a robustness check (FGR counts transfers against the
* school; GSR does not - if results hold under both, that's a stronger claim).
* -----------------------------------------------------------------------------
di as text _n "===== Model 4: robustness check, FGR as outcome ====="
regress fgr ln_revenue aid_share_of_revenue fcs no_football enrollment_thousands, robust

log close

export delimited using "results/analysis_dataset_export.csv", replace
