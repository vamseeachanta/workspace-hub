# WRK-1392: 3D Interactive Frame Viewer (HTML/three.js)

## Context

The GT1R parachute frame (`FrameGeometry3D`) can currently only be viewed via FreeCAD (requires installation) or static matplotlib PNGs. An interactive HTML viewer enables client review without software, geometry verification during iteration, and embedding in reports.

## Approach

Create a Python script that imports `FrameGeometry3D`, serializes it to JSON, and embeds it in a self-contained HTML template with three.js via CDN (jsdelivr — same pattern as `calc_report_html.py` KaTeX/Chart.js and `wall_thickness_interactive_report.py` Plotly/Tom Select). The HTML renders straight members as `CylinderGeometry`, bend members as `TubeGeometry` along a 3-point arc (reusing the sag formula from `freecad_frame_builder.py:84-101`), and BC markers as shape meshes.

## Existing Patterns (reuse)

| Pattern | Source | Reuse |
|---------|--------|-------|
| CDN script tags (jsdelivr) | `scripts/reporting/calc_report_html.py:12-15` | three.js + OrbitControls CDN URLs |
| Python HTML template with embedded data | `wall_thickness_interactive_report.py` | JSON payload injection into template |
| Color palette constants | `wall_thickness_interactive_report.py:51-57` | Assembly color dict pattern |
| Sag/arc midpoint geometry | `freecad_frame_builder.py:84-101` | Bend arc computation |
| CLI with `--output` flag | `generate_frame_cad.py` | Argparse pattern |

## Files

| Action | Path |
|--------|------|
| Create | `digitalmodel/src/digitalmodel/structural/parachute/frame_viewer_3d.py` |
| Create | `digitalmodel/tests/structural/parachute/test_frame_viewer_3d.py` |

## Implementation

### `frame_viewer_3d.py` — single module, ~200 lines

1. **`frame_to_json(geo: FrameGeometry3D) -> dict`**
   - Serialize nodes, members, connections to a plain dict
   - Include `is_bend`, `bend_clr`, assembly, bc_type for each entity
   - Compute arc midpoint for bend members (same sag formula as FreeCAD builder)

2. **`generate_viewer_html(geo: FrameGeometry3D, output_path: str) -> str`**
   - Build JSON payload via `frame_to_json`
   - three.js via CDN `<script>` tags (jsdelivr, matching existing calc report pattern)
   - CDN URLs: three.js core + OrbitControls + CSS2DRenderer addons

3. **HTML template (inline string)**
   - **Scene setup:** PerspectiveCamera, OrbitControls, ambient + directional light, grid helper
   - **Straight members:** `CylinderGeometry` oriented between start/end nodes
   - **Bend members:** `TubeGeometry` along `QuadraticBezierCurve3` (3-point arc: start → sag midpoint → end)
   - **Assembly colors:** rear_trunk = `#4488ff` (blue), under_chassis = `#ff8844` (orange), shared = `#88cc88` (green)
   - **BC markers:** fixed = red box, bolted = dark-red cone (triangle proxy), origin = gold octahedron (diamond proxy)
   - **Node labels:** CSS2DRenderer sprites, togglable
   - **Toggle panel:** HTML overlay with checkboxes for assemblies, labels, connections
   - **Controls:** OrbitControls (orbit/zoom/pan built-in)

4. **`if __name__ == "__main__"` CLI**
   - `python -m digitalmodel.structural.parachute.frame_viewer_3d [--output path.html]`
   - Default output: `outputs/frame_viewer_3d.html`

### Pseudocode — key functions

```python
def frame_to_json(geo):
    data = {"nodes": {}, "members": [], "connections": []}
    for nid, node in geo.nodes.items():
        data["nodes"][nid] = {"x": node.x, "y": node.y, "z": node.z,
                               "label": node.label, "assembly": node.assembly}
    for m in geo.members:
        entry = {"start": m.start_node, "end": m.end_node,
                 "label": m.label, "assembly": m.assembly,
                 "is_bend": m.is_bend, "bend_clr": m.bend_clr,
                 "od": m.section["OD"]}
        if m.is_bend:
            entry["arc_mid"] = compute_arc_midpoint(geo.nodes, m)
        data["members"].append(entry)
    for c in geo.connections:
        data["connections"].append({"node_id": c.node_id, "bc_type": c.bc_type,
                                     "conn_type": c.conn_type})
    return data

def compute_arc_midpoint(nodes, member):
    # Sag formula from freecad_frame_builder.py lines 84-101
    p1, p2 = nodes[member.start_node], nodes[member.end_node]
    mid = ((p1.x+p2.x)/2, (p1.y+p2.y)/2, (p1.z+p2.z)/2)
    chord_len = distance(p1, p2)
    R = member.bend_clr
    sag = R - sqrt(R**2 - (chord_len/2)**2)
    perp = perpendicular_to_chord_in_z_plane(p1, p2)
    return mid + perp * sag

def generate_viewer_html(geo, output_path):
    data = frame_to_json(geo)
    html = HTML_TEMPLATE.replace("{{FRAME_DATA}}", json.dumps(data))
    Path(output_path).write_text(html)
    return output_path
```

### Test plan

| Test | Type | Expected |
|------|------|----------|
| `test_frame_to_json_node_count` | happy | JSON has 15 nodes |
| `test_frame_to_json_member_count` | happy | JSON has 16 members |
| `test_bend_members_have_arc_mid` | happy | 4 bend members each have `arc_mid` key |
| `test_straight_members_no_arc_mid` | edge | 12 straight members lack `arc_mid` |
| `test_generate_html_creates_file` | happy | File written, >1KB, contains `<html>` |
| `test_html_contains_three_js` | happy | Output contains `THREE.Scene` |
| `test_html_contains_frame_data` | happy | Output contains node labels from geometry |
| `test_arc_midpoint_sag_value` | edge | Known bend (N6→N7, CLR=5.25) has correct sag |

## Tests/Evals

| Test | Type | Expected |
|------|------|----------|
| `test_frame_to_json_node_count` | happy | JSON has 15 nodes |
| `test_frame_to_json_member_count` | happy | JSON has 16 members |
| `test_bend_members_have_arc_mid` | happy | 4 bend members each have `arc_mid` key |
| `test_straight_members_no_arc_mid` | edge | 12 straight members lack `arc_mid` |
| `test_generate_html_creates_file` | happy | File written, >1KB, contains `<html>` |
| `test_html_contains_three_js` | happy | Output contains `THREE.Scene` |
| `test_html_contains_frame_data` | happy | Output contains node labels from geometry |
| `test_arc_midpoint_sag_value` | edge | Known bend (N6-N7, CLR=5.25) has correct sag |

## Verification

```bash
cd /mnt/local-analysis/workspace-hub
python -m pytest digitalmodel/tests/structural/parachute/test_frame_viewer_3d.py -v
python -m digitalmodel.structural.parachute.frame_viewer_3d --output /tmp/frame_viewer.html
# Open /tmp/frame_viewer.html in browser — verify orbit, labels, colors, bends
```

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-23T22:04:00Z
decision: passed
