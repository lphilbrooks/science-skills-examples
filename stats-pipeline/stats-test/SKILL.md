---
name: stats-test
description: Use whenever running a statistical comparison on the replicate-aggregated data. Encodes the decision tree, effect size, bootstrap CI, and FDR correction prescribed by AGENTS.md. Outputs a stats CSV and methods snippet for the figure.
---

# Stats Test

Runs the group comparisons that sit underneath every figure. Operates only on
replicate-aggregated data (one row per animal per condition). Producing the
output files specified in AGENTS.md §5 is part of this skill, not optional.

## Inputs

- A replicate-aggregated long-format DataFrame from `replicate-aggregate` with
  columns `target, timepoint, concentration, replicate, value, n_objects`.
- The set of comparisons to run, e.g.
  `[("Day1", "Day14"), ("1.5%", "4%")]` within each marker.
- The figure stem used to name output files.

## Procedure

### 1. Describe before you test

For each `(target, timepoint, concentration)` cell, compute:

- `n` (number of replicates)
- `median`, `q1`, `q3` (so IQR = q3 − q1)
- `min`, `max`

Store these alongside the test results.

### 2. Choose the test

Use this decision tree per comparison:

```
n per group ≤ 4 ?         → Mann–Whitney U (two-sided)        [default for this dataset]
n per group ≥ 5 ?
  ├ Shapiro–Wilk p > 0.05 on both groups AND
  │ Levene's p > 0.05                                 → Welch's t-test
  └ else                                              → Mann–Whitney U
paired design (same animal, two conditions)              → Wilcoxon signed-rank
```

Report which test was selected and why in the methods snippet.

### 3. Compute the effect size

- **Hedges' g** (Cohen's d with small-sample correction). Compute via
  `pingouin.compute_effsize(..., eftype="hedges")`.
- Always report g with a 95% confidence interval. With n ≤ 4, derive the CI
  from a bootstrap (next step), not from the analytical formula.

### 4. Bootstrap the difference of medians

```python
rng = np.random.default_rng(42)
diffs = []
for _ in range(10_000):
    a = rng.choice(group_a_values, size=len(group_a_values), replace=True)
    b = rng.choice(group_b_values, size=len(group_b_values), replace=True)
    diffs.append(np.median(b) - np.median(a))
ci_low, ci_high = np.percentile(diffs, [2.5, 97.5])
```

Use `random_state = 42` always. Report `ci_low`, `ci_high`.

### 5. Apply multiplicity correction

Within a figure, when the same comparison is run across multiple markers,
collect the raw p-values and adjust with Benjamini–Hochberg:

```python
from statsmodels.stats.multitest import multipletests
_, p_fdr, _, _ = multipletests(p_raw, method="fdr_bh")
```

`p_fdr` is what gets annotated on the plot and what `α = 0.05` is judged
against. Always keep `p_raw` in the CSV as well.

### 6. Write the stats CSV

To `analysis/results/<figure_stem>/<figure_stem>_stats.csv`, one row per
comparison:

```
marker, comparison, group_a, group_b, n_a, n_b,
median_a, iqr_a, median_b, iqr_b,
test, statistic, p_raw, p_fdr,
hedges_g, ci_low, ci_high
```

### 7. Write the methods snippet

To `analysis/results/<figure_stem>/<figure_stem>_methods.md`, a paste-ready
paragraph that includes:

- Filter applied (`qc_pass == True`, n removed).
- Outlier rule applied (cite the version of `detect-outliers`).
- Aggregation step (median per animal per condition).
- Statistical test chosen and why (decision-tree branch).
- Effect size (Hedges' g) and 95 % bootstrap CI on the difference of medians,
  with 10 000 resamples and `random_state = 42`.
- Multiplicity correction (Benjamini–Hochberg across markers).
- Software versions: Python, pandas, scipy, statsmodels, pingouin,
  statannotations.

### 8. Hand off to plotting

Return the stats DataFrame to `publication-plot`, which is responsible for
turning `p_fdr` and `hedges_g` into bracket annotations.

## Output

- A stats DataFrame (in-memory).
- `analysis/results/<figure_stem>/<figure_stem>_stats.csv`
- `analysis/results/<figure_stem>/<figure_stem>_methods.md`

## Do not

- Do not run tests on pre-aggregated `condition_summary.csv` rows — those are
  descriptive only.
- Do not drop a comparison because it is "not significant"; report all of
  them.
- Do not switch to a parametric test on the basis of normality alone when
  n ≤ 4. The test has no power to detect non-normality at that size.
- Do not omit the FDR correction when reporting a finding across markers.
