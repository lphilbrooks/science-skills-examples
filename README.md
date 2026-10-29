# science-skills-examples

Example [agent skills](https://code.claude.com/docs/en/skills) for scientific work: figure styling, CAD for lab hardware, and a statistics pipeline. Each folder is a self-contained skill (`SKILL.md` plus any scripts and references) that works with Claude Code, Codex and other tools that read `SKILL.md` skills.

These are snapshots of skills I use, shared as examples to adapt, not maintained packages.

## Skills

| Skill | What it does |
|---|---|
| [`figure-style`](figure-style) | Opinionated style for scientific plots: every data point visible, black mean ± SD, significance brackets only where significant, colour by role, stats at the level of the independent replicate. Includes `figstyle.py` (matplotlib/seaborn) and `theme_house.R` (ggplot2) helpers. |
| [`freecad-modeling`](freecad-modeling) | Text-to-CAD workflow for brackets, mounts, jigs and enclosures using the [FreeCAD Robust MCP server](https://github.com/spkane/freecad-addon-robust-mcp-server): clarify, build, validate, then export for 3D printing. Includes build, printing and validation recipes and evals. |
| [`stats-pipeline`](stats-pipeline) | Four chained skills for imaging-derived data: `detect-outliers` → `replicate-aggregate` → `stats-test` → `publication-plot`. Encodes robust outlier flagging with an audit log, aggregation to biological replicates (avoiding pseudoreplication), a test decision tree with effect sizes and FDR correction, and a replicate-level plot with annotated statistics. |

## Using them

Copy a skill folder into your agent's skills directory, for example `~/.claude/skills/<name>` or `<project>/.claude/skills/<name>`. For `stats-pipeline`, copy the four subfolders individually.

## Caveats

- `stats-pipeline` was written for one cell-morphology dataset and expects a project `AGENTS.md` and its column names (`target`, `timepoint`, `concentration`, `replicate`, `AreaShape_*`). Treat it as a template for encoding a lab's statistical rules, not a drop-in tool.
- The skills have different conventions on purpose (for example `figure-style` puts p only on brackets, while `stats-pipeline` also prints Hedges' g). Pick one per project.
- `figure-style` example images use synthetic data.

## Licence

MIT, see [LICENSE](LICENSE).