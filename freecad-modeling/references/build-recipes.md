# Build recipes — PartDesign via the Robust MCP tools (FreeCAD 1.1.x)

## Known bugs on FreeCAD 1.1.1 — use these workarounds

This setup runs FreeCAD 1.1.1 with Robust MCP server 0.6.2. Two MCP tools
crash against 1.1.x because of renamed FreeCAD properties (upstream issues
#94, #95). Don't retry the broken tools — go straight to `execute_python`.

### `pad_sketch` crashes ("Symmetric" property was renamed "Midplane")

```python
doc = FreeCAD.ActiveDocument
body = doc.getObject("Body")          # your PartDesign body
sk = doc.getObject("Sketch")          # the sketch to pad
pad = body.newObject("PartDesign::Pad", "Pad")
pad.Profile = sk
pad.Length = 10.0                     # mm
pad.Midplane = False                  # True = extrude symmetric about plane
pad.Reversed = False
sk.Visibility = False
doc.recompute()
_result_ = {"pad": pad.Name, "valid": pad.Shape.isValid(),
            "volume": pad.Shape.Volume}
```

Same pattern for Pocket (`PartDesign::Pocket`, use `pad.Reversed`/`Length` or
`Type = 1` for through-all: `pocket.Type = "ThroughAll"`).

### `get_sketch_info` crashes (removed "ExternalGeometryCount")

```python
sk = FreeCAD.ActiveDocument.getObject("Sketch")
_result_ = {
    "fully_constrained": bool(sk.FullyConstrained),
    "dof": sk.solve(),                       # 0 = solves cleanly
    "geometry": [f"{i}: {g.TypeId if hasattr(g,'TypeId') else type(g).__name__}"
                 for i, g in enumerate(sk.Geometry)],
    "constraint_count": sk.ConstraintCount,
}
```

`pocket_sketch`, `revolution_sketch` etc. may share the pad bug on 1.1.x — if
any PartDesign feature tool errors mentioning a property name, use the
`execute_python` equivalent rather than retrying.

## Standard part skeleton

Works via MCP tools directly (these are fine on 1.1.1):

1. `create_document(name="PartName")`
2. `create_partdesign_body(name="Body")`
3. `create_sketch(body_name="Body", plane="XY_Plane", sketch_name="Sketch")`
4. Geometry: `add_sketch_rectangle`, `add_sketch_circle`, `add_sketch_line`,
   `add_sketch_slot`, `add_sketch_polygon` …
5. Constraints: `constrain_distance_x/y`, `constrain_radius`,
   `constrain_horizontal/vertical`, `constrain_coincident`, `constrain_equal`…
6. Verify fully constrained (snippet above).
7. Pad via the `execute_python` workaround above.
8. Dress-up: `fillet_edges`, `chamfer_edges` (pass edge names like "Edge1";
   list them first — see edge-finding snippet below).

## Finding edges for fillets/chamfers

Edge indices shift after every feature — select by geometric property, not by
guessed name:

```python
obj = FreeCAD.ActiveDocument.getObject("Pad")
picked = []
for i, e in enumerate(obj.Shape.Edges, start=1):
    z_vals = [v.Point.z for v in e.Vertexes]
    if z_vals and all(abs(z) < 1e-6 for z in z_vals):   # bottom-face edges
        picked.append(f"Edge{i}")
_result_ = picked
```

Adapt the filter (by z-height, by curve type `type(e.Curve).__name__ ==
'Circle'`, by length) to pick the intended edges, then pass to `fillet_edges`.

## Holes

- Simple through-holes: sketch circles on a face + pocket (ThroughAll), or
  `create_hole` for parametric countersunk/counterbored holes from sketch
  points.
- Countersink for M4 flat-head: pilot Ø4.5, csk Ø9.0 × 90°.
- Remember FDM hole compensation from `printing-rules.md` — apply it to the
  sketch circle diameter, and say so in the parameter table.

## Spreadsheet-driven parameters (for parts worth re-editing)

```
spreadsheet_create(name="Params")
spreadsheet_set_cell(cell="A1", value="handle_d"), spreadsheet_set_cell(cell="B1", value=25.4)
spreadsheet_set_alias(cell="B1", alias="handle_d")
spreadsheet_bind_property(object="Sketch", property="Constraints.handle_d",
                          expression="Params.handle_d")
```

Bind the *named sketch constraints* (name them when constraining) so editing
the sheet re-drives the model. For 1–3 parameters this is optional; beyond
that it pays for itself.

## Placement and orientation

Model in the part's natural orientation (function first). If printing
orientation differs, don't rotate the model — state the print orientation in
the report; slicers handle rotation. Exception: if the user asks for a
print-ready file oriented for the bed, rotate via `set_placement` at the end.

## When PartDesign is the wrong tool

Lofted/swept organic shapes, quick throwaway geometry, or boolean-heavy CSG:
Part workbench primitives (`create_box`, `create_cylinder`, …) +
`boolean_operation` / `fuse_all` are fine. The accuracy rules don't change:
parameters in the brief, dimensions measured afterwards.
