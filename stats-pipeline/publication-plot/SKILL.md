---
name: publication-plot
description: Use whenever generating a figure from the cell morphology dataset. Produces a 300 dpi publication-style panel with replicate-level data points, bracket annotations carrying FDR-adjusted p-values and Hedges' g, and the matching stats CSV and methods snippet.
---

# Publication Plot

This skill draws the figure. Statistical content must already exist — call
`replicate-aggregate` and `stats-test` first.

## Inputs

- The replicate-aggregated DataFrame from `replicate-aggregate`.
- The stats DataFrame from `stats-test`.
- A `figure_stem` (snake_case, no extension), e.g. `target_intensity_by_condition`.

## Rcparams to set first

```python
import matplotlib as mpl
import seaborn as sns

sns.set_theme(style="whitegrid", context="paper")
mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.2,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})
```

## Palette (Okabe–Ito, colourblind safe)

```python
OKABE_ITO = {
    "Day1":    "#0072B2",
    "Day14":   "#E69F00",
    "1.5%":    "#56B4E9",
    "4%":      "#D55E00",
    "neutral": "#999999",
}
```

Map the palette to whichever variable is encoded as hue in the plot. Never
introduce a fifth colour without stating why.

## Layout rules

- Single panel: 90 mm wide, 70 mm tall.
- Multi-panel: ≤ 180 mm wide, one row per logical group (e.g. one column per
  marker for the 5-marker faceted plot).
- Title each subplot with the marker; do not put the marker in the y-label.
- Y-axis labels include units. Examples: `Target mean intensity (a.u.)`,
  `Nuclei per image`, `Cell area (px²)`.
- Y-axis starts at zero for counts and intensities.

## Mark layer (default plot)

For replicate-level comparisons:

1. `seaborn.boxplot` — `showfliers=False`, `width=0.5`, `linewidth=0.8`,
   `boxprops=dict(facecolor="white")`. Box shows median and IQR.
2. `seaborn.stripplot` over the box — `size=4`, `jitter=0.15`,
   `edgecolor="black"`, `linewidth=0.4`. One dot per animal. **This is the
   non-negotiable transparency rule** — never hide the replicates.
3. Print `n = <k>` underneath each x-tick label (use `ax.text` at
   `y = ax.get_ylim()[0] − padding`).

For object-level distribution panels:

1. `seaborn.violinplot` with `inner=None`, `cut=0`, `linewidth=0.8`.
2. Overlay replicate-median points (from the aggregated table) as a
   `stripplot` in black, `size=4`.
3. Stats brackets still come from the replicate-level stats CSV — never from
   the violins' underlying object distribution.

## Statistical annotations

Use `statannotations.Annotator`. For each comparison in the stats CSV, build a
label of the form:

```
"p = 1.3e-2  (g = 0.84)"
```

…using `p_fdr` from the stats CSV. Use scientific notation when `p < 1e-2`.
Asterisks alone are not enough — show both the exact p and the effect size.

```python
from statannotations.Annotator import Annotator

pairs   = [(("Day1", "1.5%"), ("Day14", "1.5%")), ...]   # match plot tuples
labels  = [f"p = {p:.2g}  (g = {g:.2f})" for p, g in zip(stats.p_fdr, stats.hedges_g)]

annot = Annotator(ax, pairs, data=plot_df, x="timepoint", y="value",
                  hue="concentration", order=["Day1", "Day14"])
annot.configure(test=None, text_format="simple", loc="inside",
                line_width=0.8, fontsize=9)
annot.set_custom_annotations(labels)
annot.annotate()
```

`test=None` because the test has already been run upstream; we only need to
draw the result.

## Correlation heatmap variant

When the request is a morphology correlation heatmap (AGENTS.md §7 Panel 4):

1. Build the input as a replicate-aggregated wide table — one row per
   `(target, timepoint, concentration, replicate)`, one column per
   `AreaShape_*` metric.
2. Compute `df.corr(method="spearman")` (Spearman, not Pearson, because the
   metrics are not all linearly related and Spearman is robust to outliers).
3. Plot with `seaborn.heatmap` using:
   - `cmap="RdBu_r"`, `center=0`, `vmin=-1`, `vmax=1` — diverging anchored at
     zero, as required by AGENTS.md §7.
   - `annot=True`, `fmt=".2f"`, `annot_kws={"size": 8}`.
   - `square=True`, `linewidths=0.4`, `linecolor="white"`.
4. Print n (number of replicate-rows used) in the panel title.
5. The `_stats.csv` for a heatmap contains the correlation matrix in long
   form: `var_a, var_b, rho, p_raw, p_fdr, n`.

## Caption

Generate a one-paragraph caption and save it alongside the figure (it becomes
the first paragraph of `<figure_stem>_methods.md`). Include:

- What is shown (which variable, which grouping).
- Unit of analysis (one animal per dot).
- Box = median ± IQR; whiskers = 1.5 × IQR; dots = individual replicates.
- Test, multiplicity correction, n per group.

## Save the figure

```python
out_dir = Path(f"analysis/results/{figure_stem}")
out_dir.mkdir(parents=True, exist_ok=True)
fig.savefig(out_dir / f"{figure_stem}.png", dpi=300, bbox_inches="tight",
            facecolor="white")
```

White background, not transparent. Confirm the file exists and is at least
50 kB (sanity check that the figure is not empty).

## Quality checklist (run before delivering)

- [ ] All axes have units in their labels.
- [ ] No truncated axis without stated reason.
- [ ] `n =` printed under every x-tick.
- [ ] Each replicate visible as a dot.
- [ ] Brackets show FDR-adjusted p AND Hedges' g.
- [ ] One panel per marker — markers not pooled.
- [ ] Colours match the Okabe–Ito map above.
- [ ] PNG written at 300 dpi.
- [ ] `<figure_stem>_stats.csv` exists in the same folder.
- [ ] `<figure_stem>_methods.md` exists in the same folder.

## Do not

- Do not run the statistical test inside this skill — that lives in
  `stats-test`. This skill only draws.
- Do not hide replicates behind a violin or box.
- Do not annotate with asterisks-only — always include the numeric p and g.
