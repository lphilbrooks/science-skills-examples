# 3D-printing design rules (FDM and SLA)

Apply these at **Phase 2 (brief)** — they change parameter values, not just
the export step. When the user specified printer/nozzle/material, use their
numbers; these are defaults for the common case (0.4 mm nozzle FDM, hobby SLA).

## FDM (filament)

| Rule                        | Value / guidance                                        |
| --------------------------- | ------------------------------------------------------- |
| Minimum wall thickness      | ≥ 1.2 mm (3 × 0.4 perimeters); 2–3 mm structural        |
| Minimum feature size        | ≥ 0.8 mm (2 perimeters); text ≥ 0.6 wide, 0.4 deep      |
| Hole compensation           | holes print undersize: add **+0.2–0.4 mm** to diameter, |
|                             | or note "drill to final size" for precision fits        |
| Vertical vs horizontal hole | vertical (axis ∥ Z) prints round; horizontal sags —     |
|                             | teardrop or bridge-chamfer holes > 8 mm lying down      |
| Overhangs                   | > 45° from vertical needs support — prefer chamfers     |
|                             | (45°) over horizontal overhangs where possible          |
| Bridges                     | keep unsupported bridges < ~10 mm                       |
| Clearance fits              | sliding 0.4 mm, snug 0.2 mm, press ~0.1 mm (per side:   |
|                             | halve these); test-fit feature for critical fits        |
| Elephant's foot             | 0.3–0.5 mm chamfer on bottom edges of precision parts   |
| Layer adhesion (Z weakness) | parts are weakest across layers — orient so working     |
|                             | loads are NOT tension/bending across layer lines;       |
|                             | fillet (≥ 2 mm) where walls meet base to reduce stress  |
| Screw holes                 | M3/M4/M5 clearance: 3.4/4.5/5.5 mm **before** hole      |
|                             | compensation; self-tap into plastic: M3→2.8, M4→3.7     |
| Threads                     | model threads only ≥ M8; below that use heat-set        |
|                             | inserts or self-tapping screws                          |

**Orientation note in the report**: always state the intended print
orientation (which face on the bed) and whether supports are expected.

## SLA (resin)

| Rule                     | Value / guidance                                     |
| ------------------------ | ---------------------------------------------------- |
| Minimum wall             | 1.0 mm supported, 1.5 mm unsupported                 |
| Minimum feature / hole   | features ≥ 0.3 mm; holes ≥ 0.5 mm (smaller cure shut)|
| Hollowing                | hollow bodies > ~15 mm thick; wall 2–3 mm; add       |
|                          | **2 drain holes ≥ 3 mm** at the lowest points        |
| Cupping / suction        | avoid flat-bottomed blind cavities facing the build  |
|                          | plate — vent them or reorient                        |
| Clearance fits           | 0.1–0.2 mm (much tighter than FDM)                   |
| Orientation              | parts print angled (10–30°) on supports; note that   |
|                          | support-touching faces lose finish                   |
| Large flat faces         | avoid parallel to build plate (peel forces, warping) |

## Export quality

For STL/3MF, mesh resolution matters for curved parts:

- Prefer the MCP export tools (`export_stl`, `export_3mf`). If the result
  needs finer tessellation than the defaults give, export via
  `execute_python` with explicit deflection:

```python
import Mesh, MeshPart
doc = FreeCAD.ActiveDocument
obj = doc.getObject("Body")
mesh = MeshPart.meshFromShape(Shape=obj.Shape,
                              LinearDeflection=0.05,   # mm; 0.01 for tiny precise parts
                              AngularDeflection=0.35)  # rad
mesh.write(r"C:\path\to\part.stl")
_result_ = {"points": mesh.CountPoints, "facets": mesh.CountFacets}
```

- LinearDeflection 0.05 mm is a good general default; 0.1 for large chunky
  parts, 0.01–0.02 for small precision parts. Report the setting used.
- 3MF preserves units and is preferred by modern slicers when the user has
  no stated preference between STL and 3MF.
