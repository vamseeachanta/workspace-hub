---
title: "WRK-162 Phase 2b: Inject Panel Geometry Schematic into index.html (Case 2.6)"
description: Run OrcFxAPI on test05a.owd, extract panelGeometry, build Plotly scatter, inject into existing index.html and save PNG screenshot
version: "2.0"
module: hydrodynamics/diffraction
work_item: WRK-162
session:
  id: 2026-02-17-wrk162-inject-geometry
  agent: claude-sonnet-4-6
review: pending
---

# Context

Phase 2 code changes are complete. However the existing static `benchmark/index.html` was generated
before Phase 2 — it has no geometry section. User wants to:
1. Add the multi-body panel geometry schematic to the **existing** index.html without re-running the full benchmark
2. Get a schematic screenshot (PNG)

The .owd file exists at `2.6/OrcaWave v11.0 files/test05a.owd`. OrcFxAPI is available.
No panel geometry files exist yet.

---

# Approach: One-Shot Script

Write a focused Python script (run via `uv run python`, not committed) that:
1. Loads `test05a.owd`, runs `diff.Calculate()`, extracts `diff.panelGeometry`
2. Builds a Plotly 3D Scatter3d grouped by `objectName`, marker size ∝ √area, waterplane at z=0
3. Saves `benchmark/panel_geometry.png` (kaleido; skip gracefully if absent)
4. Saves `benchmark/panel_geometry.html` (full standalone page, CDN Plotly)
5. Builds the `<div class="section">` HTML snippet
6. Injects it into existing `benchmark/index.html` just before the `</div>\n</body>` closing marker

Injection guard: skip if "Panel Geometry" already in the file (idempotent).

---

# Files Modified

| File | Action |
|------|--------|
| `docs/.../2.6/benchmark/index.html` | In-place inject geometry section |
| `docs/.../2.6/benchmark/panel_geometry.html` | Create — standalone interactive schematic |
| `docs/.../2.6/benchmark/panel_geometry.png` | Create — static screenshot (kaleido) |

Key paths (relative to `D:/workspace-hub/digitalmodel/`):
- OWD: `docs/modules/orcawave/L00_validation_wamit/2.6/OrcaWave v11.0 files/test05a.owd`
- BENCH: `docs/modules/orcawave/L00_validation_wamit/2.6/benchmark/`

---

# Script

```python
import pathlib, sys
import OrcFxAPI
import plotly.graph_objects as go

L00 = pathlib.Path("docs/modules/orcawave/L00_validation_wamit")
OWD = L00 / "2.6/OrcaWave v11.0 files/test05a.owd"
BENCH = L00 / "2.6/benchmark"
INDEX_HTML = BENCH / "index.html"

# 1. Load & solve
diff = OrcFxAPI.Diffraction()
diff.LoadData(str(OWD.resolve()))
diff.Calculate()

# 2. Extract panelGeometry
bodies = {}
for p in diff.panelGeometry:
    name = p["objectName"]
    if name not in bodies:
        bodies[name] = {"x": [], "y": [], "z": [], "area": []}
    c = p["centroid"]
    bodies[name]["x"].append(c[0])
    bodies[name]["y"].append(c[1])
    bodies[name]["z"].append(c[2])
    bodies[name]["area"].append(p["area"])

total = sum(len(b["x"]) for b in bodies.values())
for name, pts in bodies.items():
    print(f"  {name}: {len(pts['x'])} panels")

# 3. Build figure
colours = ["#1f77b4", "#ff7f0e"]
traces = []
for i, (name, pts) in enumerate(bodies.items()):
    sizes = [max(4.0, 12.0 * a**0.5) for a in pts["area"]]
    traces.append(go.Scatter3d(
        x=pts["x"], y=pts["y"], z=pts["z"],
        mode="markers",
        marker=dict(size=sizes, color=colours[i % len(colours)], opacity=0.75),
        name=name,
        text=[f"Area: {a:.3f} m\u00b2" for a in pts["area"]],
        hovertemplate="%{text}<extra>%{fullData.name}</extra>",
    ))
all_x = [v for b in bodies.values() for v in b["x"]]
all_y = [v for b in bodies.values() for v in b["y"]]
xr = [min(all_x)*1.15, max(all_x)*1.15]
yr = [min(all_y)*1.15, max(all_y)*1.15]
traces.append(go.Surface(
    x=[[xr[0],xr[1]],[xr[0],xr[1]]],
    y=[[yr[0],yr[0]],[yr[1],yr[1]]],
    z=[[0.,0.],[0.,0.]],
    showscale=False, opacity=0.15,
    colorscale=[[0,"#4fc3f7"],[1,"#4fc3f7"]],
    name="Waterplane", showlegend=False,
))

fig = go.Figure(data=traces)
fig.update_layout(
    title="Case 2.6: Multi-Body Panel Geometry (OrcFxAPI panelGeometry, symmetry-expanded)",
    height=600,
    scene=dict(xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Z (m)", aspectmode="data"),
    margin=dict(l=0, r=0, t=50, b=0),
)

# 4a. Save PNG
try:
    fig.write_image(str(BENCH / "panel_geometry.png"), width=1200, height=700, scale=2)
    print("Saved panel_geometry.png")
except Exception as e:
    print(f"PNG skipped: {e}")

# 4b. Save standalone HTML
fig.write_html(str(BENCH / "panel_geometry.html"), include_plotlyjs="cdn")
print("Saved panel_geometry.html")

# 5. Build section snippet
scatter_div = fig.to_html(full_html=False, include_plotlyjs="cdn")
section = f"""
  <div class="section">
    <h2>Panel Geometry</h2>
    <p style="color:#555;font-size:0.9em">
      OrcFxAPI panelGeometry &mdash; symmetry-expanded, {total} panels total.
      Colour-coded by body. Hover for panel area.&nbsp;
      <a href="panel_geometry.html" target="_blank">Open full page &nearr;</a>
    </p>
    {scatter_div}
  </div>"""

# 6. Inject before closing </div></body>
html = INDEX_HTML.read_text(encoding="utf-8")
MARKER = "</div>\n</body>"
if "Panel Geometry" in html:
    print("Already present — skipping injection")
elif MARKER in html:
    html = html.replace(MARKER, section + "\n" + MARKER, 1)
    INDEX_HTML.write_text(html, encoding="utf-8")
    print("Injected into index.html")
else:
    print("ERROR: closing marker not found")
```

---

# Verification

1. Open `benchmark/index.html` — "Panel Geometry" section visible below coupling tables
2. Scatter shows cylinder (blue) + spheroid (orange) with waterplane surface
3. Hover tooltip: "Area: X.XXX m²" + body name in legend
4. `panel_geometry.html` opens as standalone interactive page
5. `panel_geometry.png` exists (or PNG-skip note printed)
