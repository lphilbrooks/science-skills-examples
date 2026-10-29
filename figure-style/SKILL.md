---
name: figure-style
description: A house style for scientific graphs, charts and figures in papers, theses, reports, talks and posters. Use whenever creating, restyling or reviewing any plot of experimental data (matplotlib, seaborn, ggplot2, Prism-matched figures, charts for PowerPoint). Covers chart choice, how data and summary statistics are shown, significance annotation, colour, typography, layout and export. Takes precedence over generic dataviz skills.
---

# Figure style

**In one line:** clean, white, GraphPad-Prism-like plots where every data point is visible,
the summary statistic is a plain black mean ± SD, colour carries meaning, and only what
matters is annotated.

Visual target: `examples/figstyle_helper_example.png` (synthetic data, produced by `scripts/figstyle.py`).

## 1. Core rules (always apply)

1. **Only annotate significant results.** Never draw "ns" brackets or mark non-significant comparisons.
2. **A significance bracket carries the p value and nothing else** (`p = 0.009`). No test
   names, effect sizes or extra text on the figure; those go in the caption, text or stats table.
   Stars (`*`, `**` …) only when matching an existing figure series that already uses them.
3. **Let the design show n.** If replicates are already distinguishable by colour tone or
   shape, don't add redundant n labels to the plot; state n in the caption.
4. **Statistics at the level of the independent replicate** (e.g. animal, donor, batch), never on
   pooled technical measurements. Outlier removal is logged, never silent.
5. **Figures and text must agree.** Every number, n and p value on a figure must match the
   results text and caption. When regenerating, trace the figure back to its script and data.
6. **Slides: plain white background, simple.** No decorative templates behind data.

## 2. How data are shown

- **Every data point is visible.** Never a bare bar or bare mean. If bars are used, points sit on top.
- **Summary = black mean ± SD**, centred over the points: a horizontal mean line spanning the
  point cloud plus a capped SD whisker, drawn on top of the points. Use SEM only where a field
  convention demands it (e.g. dose–response curves) and say so in the caption.
- **Nested data** (many technical measurements within a few independent replicates): show all
  measurements, colour them by replicate **tone** within the group colour (dark → light shades of
  one hue), and base the summary and statistics on replicate means.
- **Reference values are drawn, not described:** a dotted grey horizontal line for a control,
  baseline or threshold, labelled directly at its end ("Control", "50 %", "Seeding density").
  A target range is a shaded band around a line.
- **Honest axes:** start at zero for counts, percentages and intensities. Use a log axis when
  values span orders of magnitude, with plain tick labels (0.1, 1, 10, 100).

## 3. Choosing the chart

| Data | Default chart |
|---|---|
| Few groups, small n (≤ ~10) | Scatter-dot plot + black mean ± SD (**house default**) |
| Many measurements nested in few replicates | Swarm/strip coloured by replicate tone + mean ± SD |
| Larger n where the distribution shape matters | Outline-only violin (no fill), dashed median, dotted quartiles; or dot plot |
| Continuous response vs dose/concentration | Log-x, mean ± error points + fitted curve, reference line at the key threshold |
| Time course | Points joined by lines at the real timepoints |
| Spectra, sweeps, curves over frequency/strain | Lines (log–log where appropriate), mean line + shaded ± SD band, direct labels |
| Representative raw curves | One clean line per group, dashed construction lines + text for derived quantities |
| Many variables × conditions | Annotated heatmap (diverging map centred on 0 for ratios; fixed-range map for percentages) |
| Headline number on a slide | Bar with points, bold value label above, `n = k` inside the bar base |
| Two continuous variables | Scatter coloured by group with per-group fit line |

Avoid: 3D, pie charts, dual y-axes unless unavoidable, stacked bars for comparisons,
box plots hiding small n.

## 4. Colour

Pick colour by **role**, not decoration. Full guidance and hex values: `references/palettes.md`.

- **Two contrasting groups:** blue vs red. Blue = baseline, control-like, lower, softer, younger;
  red = changed, treated-like, higher, stiffer, older. Keep that mental model when inventing pairs.
- **Treatment vs control on slides:** one strong accent (teal) vs neutral grey.
- **Replicates within a group:** tones of the group's hue, dark → light.
- **A second factor:** marker shape (● ■ ▲) before adding more hues.
- **Ordered levels (doses, timepoints, concentrations):** a sequential map (viridis) or a small
  ordered set; keep the order the same everywhere.
- **Heatmaps:** diverging blue–white–red centred on zero for ratios/fold change; fixed 0–100
  red–yellow–green for viability-type percentages with values printed in cells.
- **Grey** for references, controls and anything secondary.
- **Consistency beats everything:** once a variable has a colour in a project, it keeps it in
  every panel, figure, slide and poster. Check sibling figures before choosing.
- No more than ~5 hues per figure; no neon/dark themes; colour-blind check red–green pairs
  (add shape or lightness difference).

## 5. Typography and layout

- Sans-serif (Arial/Helvetica), black text, sizes set at **final** size: ~7–9 pt for journals,
  ~10 pt thesis, ≥ 12–14 pt slides. Never rescale a figure after export.
- **Short bold title** naming the measurement ("Failure Stress", "Nuclei Count"), not a sentence
  and not auto-generated text like "Modulus by Group (Points, Mean ± SD)".
- Axis labels with units in parentheses, SI, Unicode superscripts: `Stress (N/mm²)`,
  `Concentration (µg mL⁻¹)`. British spelling.
- Open axes (left and bottom only), no gridlines on categorical plots; faint grid only on log–log
  spectra.
- Short category labels; rotate 45° when crowded; drop the x-axis title when categories explain themselves.
- Frameless legends, or better, direct labels.
- Bold panel letters A, B, C top-left (A-1, A-2 for linked sub-panels); consistent sizes across panels.
- Order groups logically: control/baseline first, then increasing dose/time/severity.

## 6. Slides and posters

- Slide title states the finding ("The antibody costs some conductivity").
- One main chart per slide, large; 2–4 short bullets beside it.
- Small grey italic caption under the chart: what is plotted, statistic, n, meaning of reference lines.
- Orient the audience: readable axes; one line on how to read unusual charts; highlight boxes
  on heatmaps around the result being discussed.
- Comparisons on slides may use a light grey italic note on a bracket ("~4× lower").

## 7. Workflow and deliverables

1. Tidy data → aggregate to independent replicates → run stats and keep p values in a table.
2. Plot each panel separately (`scripts/figstyle.py` or `scripts/theme_house.R`).
3. Export each panel as **PNG (600 dpi print / 300 dpi slides, white background) + SVG or PDF**
   with editable text. Offer an unannotated `_clean` version when you will assemble or
   annotate in PowerPoint.
4. Assemble multi-panel figures in PowerPoint or matplotlib; keep fonts equal across panels.
5. Keep the plotting script beside its output, named after the figure, with the data source and
   stats source noted at the top, so every figure can be regenerated.
6. Draft the caption: what each panel shows, statistic, n (independent replicates), test, exact
   p for significant results, meaning of colours/tones/reference lines.
7. **Render and look at the image before handing it over.**

## 8. Checklist

- [ ] All points visible; mean ± SD centred and on top
- [ ] Only significant comparisons annotated, with p only
- [ ] Colours by role and consistent with sibling figures
- [ ] Units on axes; log scale where data span decades; zero baseline where required
- [ ] Short bold title, panel letters, British spelling, legible at final size, no overlaps
- [ ] n and statistic in the caption; stats on independent replicates; figure matches text

## Quick start

```python
import sys; sys.path.insert(0, r"<skill>/scripts")
import matplotlib.pyplot as plt, figstyle as fs
fs.apply("paper")                                     # "paper" | "thesis" | "slide"
fig, ax = plt.subplots(figsize=fs.size("single"))
fs.dot_plot(ax, df, x="group", y="value", order=["Control", "Treated"],
            colors={"Control": fs.BLUE, "Treated": fs.RED}, rep="replicate")
fs.finish(ax, title="Modulus", ylabel="Modulus (kPa)")
fs.sig_bracket(ax, 0, 1, p=0.009)                     # silently skipped if p ≥ 0.05
fs.panel_label(ax, "A")
fs.save(fig, "fig1a_modulus", outdir="figures", clean_axes=[ax])
```

R: `source("<skill>/scripts/theme_house.R"); theme_set(theme_house("paper"))`, then
`geom_dot_mean_sd()`, `scale_fill_manual(values = pal_pair)`, `sig_bracket()`, `ref_line()`, `save_fig()`.
