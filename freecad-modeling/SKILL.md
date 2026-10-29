---
name: freecad-modeling
description: Disciplined text-to-CAD workflow for the FreeCAD Robust MCP server (mcp__freecad__* tools). Use whenever the user asks to design, model, create, or modify a 3D part, bracket, enclosure, mount, spacer, jig, adapter, replacement part, or any physical object in FreeCAD — or asks for an STL/STEP/3MF for 3D printing or machining — even if they don't say "FreeCAD" or "CAD". Covers requirement clarification, parametric PartDesign modeling, dimensional validation, visual review, printability rules (FDM/SLA), and export. Also use when asked to inspect, measure, or fix an existing FreeCAD model.
---

# FreeCAD parametric modeling with the Robust MCP bridge

Turn a text description into an accurate, validated, parametric FreeCAD model.
The core discipline: **clarify once, plan with numbers, build parametrically,
measure everything you claimed, look at the part, then export for the actual
use case.** A dimension you did not measure is a dimension you do not know.

## Phase 0 — Preflight

Probe the connection with `get_freecad_version` (NOT `get_connection_status`,
whose cached flag reads stale-false on this setup even when the bridge is up).
If the probe fails, FreeCAD isn't running: ask the user to open FreeCAD (the
MCP bridge auto-starts with it) — do not attempt workarounds.

Note `gui_available` from the probe: screenshots and visual review (Phase 5)
only work in GUI mode; in headless mode replace them with extra geometric
checks and say so in the report.

Work in a **new document named after the part** (`create_document`). Never
modify or close documents you didn't create unless asked.

## Phase 1 — Extract the spec, then ask ONE batched round of questions

Read the request and fill this mental checklist:

| Slot                  | Examples                                            |
| --------------------- | --------------------------------------------------- |
| Use case / function   | what does it hold/do, indoor/outdoor, load-bearing? |
| Manufacturing method  | FDM print, SLA print, CNC, laser, just a render?    |
| Critical dimensions   | sizes that must fit something, with units           |
| Fit / mating parts    | what does it attach to, clearance or press fit?     |
| Quantity of variants  | one part, a family, an assembly?                    |

**If use case, manufacturing method, or a fit-critical dimension is missing or
ambiguous, stop and ask — once.** Batch every question into a single round
(max ~4 questions; use AskUserQuestion when available, otherwise plain text).
The purpose is accuracy, not interrogation: a phone stand for FDM printing and
a phone stand for CNC aluminium are different models, and guessing wrong wastes
the whole build. Typical round for "design me a phone stand":

1. "What's the use case — desk stand for daily use? Which phone/size?"
2. "Is this for 3D printing? FDM or SLA (resin)?" — this changes wall
   thicknesses, tolerances, and orientation choices.
3. "Any dimension constraints (footprint, viewing angle)?"

Everything not answered (or if the user can't be asked): pick a sensible value,
and **record it as an explicit assumption that appears in the final report**.
Do not ask a second round; do not ask questions whose answer doesn't change
the geometry.

Defaults when unspecified: millimetres; origin at part centre on XY plane,
+Z up; single closed solid; parametric PartDesign body.

## Phase 2 — Write the design brief (before touching any tool)

Post a short brief in your response, then follow it:

```
Part: broom-handle wall hook
Use case: holds 25 mm broom handle, FDM printed, PETG
Parameters: handle_d=25.4 (25+0.4 FDM clearance), wall_t=4, hook_depth=30, ...
Origin: back face centre on XZ plane, +Y out of wall
Expected bounding box: ~40 x 45 x 60 mm
Features: C-hook profile pad, 2x M4 countersunk holes @ 40 mm spacing
Validation targets: opening = 25.4 ±0.1, hole Ø4.5, csk Ø9, bbox as above
Assumptions: PETG, 0.4 nozzle, screws into wall plugs
```

Parameters get names and values here — the model must be built from these
numbers, not from improvised magic values. If the use case is 3D printing,
**read `references/printing-rules.md` now** and apply its clearances and
minimums to the parameter values (e.g. hole compensation) *at this stage*,
not as an afterthought.

## Phase 3 — Build parametrically

Read `references/build-recipes.md` before building — it contains working
patterns and the **known-bug workarounds for FreeCAD 1.1.x** that this exact
setup needs (`pad_sketch` and `get_sketch_info` MCP tools crash on 1.1.1;
use the `execute_python` recipes instead).

Guidelines:

- Prefer **PartDesign**: body → sketch → constrain → pad/pocket → dress-up.
  Use Part primitives + booleans only for genuinely simple one-off shapes.
- Fully constrain sketches and verify it (`sketch.FullyConstrained` via
  `execute_python`) — an unconstrained sketch is a part that moves when
  recomputed.
- Drive geometry from the brief's parameters. For parts with several coupled
  parameters, put them in a spreadsheet (`spreadsheet_create`,
  `spreadsheet_set_alias`, `spreadsheet_bind_property`) so the part stays
  editable.
- `recompute` after each feature; if an operation fails, fix or undo it
  (`undo_if_invalid`) before stacking more features on top.

## Phase 4 — Measure what you claimed

Deterministic checks first, against the brief's validation targets. Use the
snippets in `references/validation-recipes.md`. Minimum bar for every part:

1. `validate_document` — no invalid/error objects.
2. Shape is a single closed solid, `isValid()`, `Volume > 0`.
3. **Bounding box** matches the brief's expectation (±1 mm or stated).
4. **Every fit-critical dimension measured** — hole diameters from actual edge
   geometry, wall thicknesses, spacings. Report measured vs target in a table.

If a check fails: change the smallest responsible feature, recompute, re-run
that check. Don't report success from intent — only from measurement.

## Phase 5 — Look at the part (GUI mode)

Geometry checks can pass on a part that is obviously wrong. Take screenshots
(`get_screenshot`) — isometric first, then the orthographic view that best
shows each feature (top for hole layout, front/right for profiles). Critique
against the request: proportions, feature presence, placement, orientation,
anything that would make the user say "that's not what I meant".

Fix the smallest thing, recompute, re-check. If after **3 refine cycles** the
model still doesn't converge on the intent, stop and ask the user with a
screenshot rather than burning more cycles.

## Phase 6 — Deliver for the actual use case

- Save the document (`save_document`) — path in the user's working directory
  or where they asked.
- Export per manufacturing method:
  - **FDM/SLA printing** → STL or 3MF (`export_stl` / `export_3mf`); mesh
    quality guidance in `references/printing-rules.md`. State the intended
    print orientation and any support implications.
  - **CNC / general engineering / "send to someone"** → STEP (`export_step`).
  - Unknown → FCStd + STEP.
- Final report must contain: files produced (paths), the parameter table,
  **assumptions made**, the measured-vs-target validation table, screenshots
  taken, and anything you'd flag for a human check (fit tolerances, print
  orientation, untested load paths).

## Non-negotiables

- One batched clarification round when use case / method / fit-critical dims
  are missing — never zero (silent guessing on fit-critical work) and never
  an interrogation drip.
- Named parameters, fully constrained sketches, closed solids.
- Never state a dimension in the report that you didn't measure in Phase 4.
- Assumptions are always surfaced, never silent.
- If FreeCAD isn't reachable, say so and stop — don't fake outputs.

## References

- `references/printing-rules.md` — load when use case is 3D printing (FDM or
  SLA design rules, tolerances, hole compensation, export mesh quality).
- `references/build-recipes.md` — load before Phase 3 (PartDesign patterns,
  sketch constraint recipes, FreeCAD 1.1.x bug workarounds, spreadsheets).
- `references/validation-recipes.md` — load at Phase 4 (measurement snippets:
  bounding box, hole diameters, wall thickness, solidity, report template).
