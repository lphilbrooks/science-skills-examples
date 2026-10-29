---
name: replicate-aggregate
description: Use before any group-level statistical test on this dataset. Aggregates object-level or image-level data to one value per biological replicate per condition, which is the unit of analysis enforced by AGENTS.md. Prevents pseudoreplication.
---

# Replicate Aggregate

The dataset is hierarchical: many objects per image, many images per animal, a few
animals per condition. Treating each object (or image) as independent inflates the
effective sample size and produces falsely small p-values. This skill collapses
the data to one value per `(target, timepoint, concentration, replicate)` so
that the unit of analysis is the animal.

## When to use

- Always, before running `stats-test`.
- Always, before drawing replicate-level points on a plot.

## When not to use

- For pure distribution plots (e.g. cell-area violins) you may show all
  objects, but the statistical comparison drawn on top of the plot must still
  use the replicate-aggregated values.

## Inputs

A cleaned DataFrame from `detect-outliers`, with at minimum the columns
`target`, `timepoint`, `concentration`, `replicate`, and the variable(s) being
analysed.

## Procedure

1. **Confirm the grouping keys.** Default: `["target", "timepoint",
   "concentration", "replicate"]`. If the user specifies a different question
   (e.g. pooling across markers), update the keys explicitly and state it.

2. **Choose the aggregator.**

   | Variable type             | Default aggregator                       |
   |---------------------------|------------------------------------------|
   | Object-level morphology   | `median`                                 |
   | Object-level intensity    | `median`                                 |
   | Image-level counts        | `sum` (across images of a replicate) or `mean` |
   | Image-level intensity     | `mean` of image means                    |

   Median is the default for object-level data because object distributions are
   right-skewed and contain residual segmentation noise even after outlier
   filtering.

3. **Aggregate.** Pseudocode:

   ```python
   keys = ["target", "timepoint", "concentration", "replicate"]
   agg = (
       df.groupby(keys, dropna=False)
         .agg(value=(variable, "median"),
              n_objects=(variable, "size"),
              q1=(variable, lambda x: x.quantile(0.25)),
              q3=(variable, lambda x: x.quantile(0.75)))
         .reset_index()
   )
   ```

4. **Carry sample size forward.** Always retain `n_objects` (or `n_images`) so
   the methods snippet can disclose how much data each replicate point
   summarises.

5. **Check group balance.** Print a `target × timepoint × concentration`
   contingency table of replicate counts. If any cell has `n < 2` replicates,
   flag it: comparisons against that cell are descriptive, not inferential.

6. **Save the aggregated table** to
   `analysis/results/<figure_stem>/<figure_stem>_replicate_table.csv` so the
   exact numbers underlying every test are auditable.

## Output

A long-format DataFrame with columns
`target, timepoint, concentration, replicate, value, n_objects, q1, q3`,
ready for `stats-test` and `publication-plot`.

## Do not

- Do not aggregate across `target` unless explicitly asked.
- Do not aggregate to the image level and then pass that to `stats-test` —
  always go all the way to the replicate.
- Do not use `mean` for object-level morphology; right-skew makes the mean
  unrepresentative.
