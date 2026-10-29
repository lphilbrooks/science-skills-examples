---
name: detect-outliers
description: Use whenever cleaning the morphology or image-summary data before statistical testing or plotting. Covers physical-constraint checks, segmentation-noise floors, and robust within-group outlier flagging.
---

# Detect Outliers

This procedure must run before aggregation (`replicate-aggregate`) and before
any statistical test. It produces an audit trail so every removed row remains
traceable.

## Inputs

- `image_summary.csv` or `object_subset.csv` (after `qc_pass == True` filter)
- The grouping keys for "within group": `target`, `timepoint`, `concentration`,
  `object_type` (for object-level data only).

## Procedure

### 1. Physical constraint checks (always remove)

Flag and **remove** rows that violate the physical bounds of the measurement.
Mark these as `reason = "image_analysis_anomaly"`.

| Column                    | Valid range  |
|---------------------------|--------------|
| `AreaShape_FormFactor`    | (0, 1]       |
| `AreaShape_Eccentricity`  | [0, 1]       |
| `AreaShape_Solidity`      | (0, 1]       |
| `AreaShape_Area`          | > 0          |
| Any `*_intensity` column  | ≥ 0          |

### 2. Segmentation-noise floor (object-level only)

Objects with `AreaShape_Area < 50` pixels are almost certainly segmentation
debris. Remove them with `reason = "segmentation_noise"`. Document the
threshold value in the methods snippet.

### 3. Within-group robust outlier flag

For each numeric variable to be tested, compute outlier bounds **per group**
(group = `target × timepoint × concentration × object_type`):

- **Tukey IQR fences:** `[Q1 − 1.5·IQR, Q3 + 1.5·IQR]`
- **Median Absolute Deviation:** `|x − median| / (1.4826 · MAD) > 3.5`

A value is flagged if **both** rules agree. The double rule reduces false
positives on heavy-tailed but legitimate distributions. Mark these as
`reason = "robust_outlier"`.

Do **not** use Mean ± 3·SD. Morphology distributions are right-skewed and the
SD is itself inflated by outliers.

### 4. Image-level low-yield flag

For `image_summary.csv`, flag images with `count_nuclei < 3` as
`reason = "low_segmentation_yield"`. Discuss with the user before removing —
sometimes these are biologically meaningful (e.g. cell death conditions).

### 5. Write the audit log

Append every flagged row to `analysis/outlier_audit.csv` with columns:

```
timestamp, source_file, row_index, target, timepoint, concentration,
replicate, image_number, object_number, variable, value, group_median,
group_iqr, reason, action
```

`action` is one of `"removed"`, `"flagged_kept"`, `"reviewed_kept"`.

### 6. Report

Print to console and include in the methods snippet:

- Total rows in, total rows out.
- Removals by reason (count per category).
- Conditions where > 10% of rows were removed (these need a human eye).

## Output

A cleaned DataFrame ready for `replicate-aggregate`, plus a row appended to
`analysis/outlier_audit.csv` for every removed row.

## Do not

- Do not silently filter.
- Do not apply Mean ± k·SD.
- Do not remove an entire condition because of a few outliers — flag and report.
- Do not re-run the outlier filter on already-aggregated replicate-level data.
