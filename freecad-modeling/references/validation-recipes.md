# Validation recipes — measure what you claimed

Run at Phase 4, against the brief's validation targets. All snippets go
through `execute_python`. The point: the report's numbers come from these
measurements, never from the values you *intended* to model.

## 1. Document health

Use the `validate_document` MCP tool first (checks invalid shapes / error
states across all objects).

## 2. Solidity + volume + bounding box (the baseline check)

```python
doc = FreeCAD.ActiveDocument
obj = doc.getObject("Body")          # or the final feature/part
s = obj.Shape
bb = s.BoundBox
_result_ = {
    "is_valid": s.isValid(),
    "shape_type": s.ShapeType,
    "solids": len(s.Solids),          # expect 1 for a single part
    "closed": s.isClosed() if s.ShapeType != "Compound" else None,
    "volume_mm3": round(s.Volume, 2), # must be > 0
    "bbox_mm": [round(bb.XLength, 3), round(bb.YLength, 3), round(bb.ZLength, 3)],
}
```

Compare `bbox_mm` with the brief's expected bounding box. A wildly different
bbox means a sketch scaled wrong, a pad in the wrong direction, or units
confusion — catch it here, not in the screenshot.

## 3. Hole diameters (measured from real geometry)

```python
obj = FreeCAD.ActiveDocument.getObject("Body")
holes = []
for i, f in enumerate(obj.Shape.Faces, start=1):
    surf = f.Surface
    if type(surf).__name__ == "Cylinder":
        holes.append({"face": f"Face{i}", "diameter": round(surf.Radius * 2, 3),
                      "axis": [round(c, 2) for c in surf.Axis]})
_result_ = holes
```

Match each expected hole (count + diameter) against this list. Circular
sketch edges can also be read from `e.Curve.Radius` on `Circle`-type edges.

## 4. Wall thickness / local distances

For a specific wall, measure between the two faces that bound it:

```python
import Part
obj = FreeCAD.ActiveDocument.getObject("Body")
f_outer = obj.Shape.Faces[0]          # pick faces by position/normal, print
f_inner = obj.Shape.Faces[3]          # candidates first if unsure
d = f_outer.distToShape(f_inner)[0]
_result_ = {"wall_mm": round(d, 3)}
```

`distToShape` also measures clearances between separate objects (fit checks
in multi-part documents).

## 5. Fully-constrained sketches

```python
sk = FreeCAD.ActiveDocument.getObject("Sketch")
_result_ = {"fully_constrained": bool(sk.FullyConstrained), "dof": sk.solve()}
```

## Report template

End the job with this table (measured values only):

```
| Check                  | Target        | Measured      | Pass |
| ---------------------- | ------------- | ------------- | ---- |
| Single valid solid     | yes           | yes           | ✔    |
| Bounding box (mm)      | 60 × 40 × 8   | 60.0 × 40 × 8 | ✔    |
| Corner holes           | 4 × Ø5.0      | 4 × Ø5.0      | ✔    |
| Centre bore            | Ø20.0         | Ø20.0         | ✔    |
| Sketch constrained     | fully         | fully (dof 0) | ✔    |

Assumptions: <everything guessed in Phase 1/2>
Files: <FCStd + exports with full paths>
Print orientation (if printing): <face on bed, support note>
```

A failed row is not a reporting problem, it's a modeling problem: fix the
feature and re-measure. If a target genuinely can't be met, say why instead
of quietly dropping the row.

## Screenshots (Phase 5, GUI only)

`set_view_angle(view="isometric")` → `fit_all` → `get_screenshot`. Then the
view that best shows each feature: `top` for hole layouts, `front`/`right`
for profiles and heights, `bottom` for underside features. Critique order:
overall proportions → feature presence → placement/symmetry → orientation.
In headless mode (`gui_available: 0`), skip and compensate with extra
measurements (e.g. hole positions via `surf.Center`), and note it.
