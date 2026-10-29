# Colour by role

Constants live in `scripts/figstyle.py` and `scripts/theme_house.R`.

| Role | Colour | Notes |
|---|---|---|
| Contrasting pair, group 1 (baseline / control-like / lower) | blue `#0000FF` (Prism) or `#1F77B4` (softer) | |
| Contrasting pair, group 2 (changed / treated-like / higher) | red `#FF0000` (Prism) or `#D62728` | |
| Third category when blue/red are taken | green `#008000` | |
| Accent for the key condition on slides | teal `#0E7C7B` | pairs with grey control |
| Control / bare / secondary | grey `#9AA0A6` | |
| Ink for text, whiskers, dark bars | `#2B2B2B` or black | |
| Reference lines and bands | grey `#808080`, band alpha 0.25 | |
| Replicate tones within a group | shades of the group hue, dark → light | `plt.cm.Blues/Reds/Greens` 1.0 → 0.45 |
| Ordered levels (dose, time) | `viridis` (end 0.9) or a fixed small ordered set | same order everywhere |
| Ratios / fold change heatmap | `RdBu_r`, centred on 0, symmetric limits | |
| Percentage heatmap (e.g. viability) | `RdYlGn`, fixed 0–100, values printed | white text on dark cells |
| Raw intensity / QC heatmap | `inferno` | |
| Many unrelated categories | Okabe–Ito `#0072B2 #E69F00 #009E73 #D55E00 #CC79A7 #56B4E9 #F0E442` | colour-blind safe |

Principles
- A variable keeps its colour across every figure in a project.
- Prefer shape or lightness for a second factor over extra hues.
- Red vs green alone is never the only cue.
- Avoid neon/dark-theme palettes, rainbow/jet, and seaborn defaults in final figures.
