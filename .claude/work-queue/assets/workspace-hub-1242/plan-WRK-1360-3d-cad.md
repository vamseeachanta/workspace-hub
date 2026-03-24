# WRK-1360: 3D CAD Geometry (FreeCAD) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a 3D FreeCAD model of the GT1R R35 parachute mounting frame (rear trunk + under-hood assemblies) with tube members, connections, and STEP export for downstream meshing.

**Architecture:** Pure-Python geometry module (`frame_geometry_3d.py`) defines 3D node coordinates and member connectivity for both assemblies. Separate FreeCAD builder (`freecad_frame_builder.py`) consumes geometry to create Part::Cylinders along member centerlines, adds connection markers, and exports STEP. This separation means geometry tests run without FreeCAD, while FreeCAD tests run only on ace-linux-2.

**Tech Stack:** Python 3.11, FreeCAD 0.21.2 (ace-linux-2), pytest, `freecadcmd` for headless execution

**Runtime note:** FreeCAD is installed on ace-linux-2 only. Code is on ace-linux-1 (SSHFS mount at `/mnt/workspace-hub`). Run FreeCAD scripts locally on ace-linux-2; commit via `ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git ...'`.

---

## Geometry Reference (from hand sketches + photos)

### Assembly 1 — Rear Trunk Frame (Page 1)

Coordinate system: X = transverse (left-right), Y = longitudinal (front-back), Z = vertical (up positive). Origin at left C3 mount.

**Top view (horizontal bar):**
- N0 (0, 0, 0) — left C3 mount (weld, fixed BC)
- N1 (6, 0, 0) — left bar-strut junction (C0 weld)
- N2 (18, 0, 0) — center bar, C1 bolt+pin
- N3 (30, 0, 0) — right bar-strut junction (C0 weld)
- N4 (36, 0, 0) — right C3 mount (weld, fixed BC)
- N5 (18, 0, -7.25) — coupler pin (load application point)

**Members:**
- M0: N0→N1 (bar_left_end, 6")
- M1: N1→N2 (bar_left_center, 12")
- M2: N2→N3 (bar_center_right, 12")
- M3: N3→N4 (bar_right_end, 6")
- M4: N1→N5 (v_strut_left, ~14.0" = √(12²+7.25²))
- M5: N3→N5 (v_strut_right, ~14.0")

**Parachute arm (from photos):**
- N6 (18, -Y_arm, -7.25) — bracket at rear bumper (extends rearward from coupler pin through bumper cutout)
- M6: N5→N6 (parachute_arm) — the tubular arm visible in photos, connects coupler to rear mount plate

Note: Y_arm dimension TBD — estimated ~18" from photos. The arm is the curved copper-colored tube visible in bracket-closeup-rear-mount.jpeg.

### Assembly 2 — Under-Hood Frame (Page 2)

Located forward of the trunk frame. Connected via the vehicle chassis (load path through frame rails from C3 mounts to B1 bolted connection).

**Front view:**
- N7 (X_left, Y_hood, Z_hood) — left end of under-hood horizontal bar (C2 weld to chassis)
- N8 (X_left + 14, Y_hood, Z_hood) — right side, near B1 connection
- N9 (X_left + 14 + 5, Y_hood, Z_hood - 1) — B1 bolted connection (6 bolts to chassis/subframe)

**Members:**
- M7: N7→N8 (hood_bar_main, 14")
- M8: N8→N9 (hood_bar_end, ~5.1" with 1" vertical offset)

**Top view (curved member):**
- Curved member at 150° included angle connecting to P1 pinned BC
- N10: P1 pinned boundary condition point
- M9: N8→N10 (curved_arm, with 150° arc)
- Additional: 8" vertical dimension, 6"/4"/5" sub-dimensions (VF notation)

**Connection to Assembly 1:** Nodes N0 and N4 (C3 mounts) connect through the vehicle frame rails to N7/N9 region. For the structural model, this is modeled as rigid links or spring connections representing frame rail stiffness.

### Dimensions with uncertainty

| Dimension | Value | Source | Confidence |
|---|---|---|---|
| Bar total width | 36" | Sketch (6+12+12+6) | High |
| Coupler pin offset | 7.25" | Sketch annotation | High |
| Tube OD | 1.5" | Sketch side view "1.5 (H)" | Medium |
| Tube CL | 12" | Sketch side view "12 CL" | Medium |
| Under-hood bar | 14" | Sketch "1/4 → 5" | Medium |
| Under-hood offset | 1" | Sketch annotation | Medium |
| Parachute arm length | ~18" | Photo estimate | Low |
| Curved member angle | 150° | Sketch "150° eth" | Medium |

---

## File Structure

| Action | File | Responsibility |
|--------|------|---------------|
| Create | `src/digitalmodel/structural/parachute/frame_geometry_3d.py` | 3D node coordinates, member connectivity, connection metadata for both assemblies. Pure Python — no FreeCAD dependency. |
| Create | `src/digitalmodel/structural/parachute/freecad_frame_builder.py` | Consumes `FrameGeometry3D`, creates FreeCAD Part objects (tubes along centerlines), exports STEP/IGES. |
| Create | `tests/structural/parachute/test_frame_geometry_3d.py` | Geometry validation: dimensions, symmetry, member lengths, connection types. No FreeCAD needed. |
| Create | `tests/structural/parachute/test_freecad_frame_builder.py` | FreeCAD integration: document creation, tube shapes, STEP export. Skipped if FreeCAD unavailable. |
| Modify | `src/digitalmodel/structural/parachute/__init__.py` | Add imports for new modules. |

---

## Task 1: 3D Geometry Data Model

**Files:**
- Create: `src/digitalmodel/structural/parachute/frame_geometry_3d.py`
- Create: `tests/structural/parachute/test_frame_geometry_3d.py`

- [ ] **Step 1: Write failing test — node count and assembly structure**

```python
# tests/structural/parachute/test_frame_geometry_3d.py
"""
Tests for 3D frame geometry — GT1R parachute mounting frame.
Both assemblies: rear trunk frame (Page 1) + under-hood frame (Page 2).
"""
import math
import pytest
from digitalmodel.structural.parachute.frame_geometry_3d import (
    build_gt1r_frame_3d,
    FrameGeometry3D,
    Node3D,
    Member3D,
)


class TestFrameGeometry3DStructure:
    def setup_method(self):
        self.geo = build_gt1r_frame_3d()

    def test_returns_frame_geometry_3d(self):
        assert isinstance(self.geo, FrameGeometry3D)

    def test_has_rear_and_hood_assemblies(self):
        labels = {m.assembly for m in self.geo.members}
        assert "rear_trunk" in labels
        assert "under_hood" in labels

    def test_rear_trunk_node_count(self):
        rear_nodes = self.geo.assembly_nodes("rear_trunk")
        assert len(rear_nodes) >= 6  # N0..N5 minimum

    def test_rear_trunk_member_count(self):
        rear_members = self.geo.assembly_members("rear_trunk")
        assert len(rear_members) >= 6  # M0..M5 minimum
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/test_frame_geometry_3d.py -v`
Expected: FAIL — ImportError (module doesn't exist yet)

- [ ] **Step 3: Write minimal data model + rear trunk geometry**

```python
# src/digitalmodel/structural/parachute/frame_geometry_3d.py
"""
ABOUTME: 3D geometry for GT1R parachute frame — both assemblies
ABOUTME: Pure Python node/member model, no FreeCAD dependency
"""
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from digitalmodel.structural.parachute.frame_model import (
    CHROMOLY_4130,
    tube_section_properties,
)


@dataclass
class Node3D:
    id: int
    x: float
    y: float
    z: float
    label: str = ""
    assembly: str = ""


@dataclass
class Connection:
    node_id: int
    conn_type: str  # C0, C1, C2, C3, B1, coupler_pin, P1
    bc_type: str    # "fixed", "pinned", "free", "bolted"
    description: str = ""


@dataclass
class Member3D:
    id: int
    start_node: int
    end_node: int
    label: str
    assembly: str
    section: Dict[str, float] = field(default_factory=dict)

    def length(self, nodes: Dict[int, Node3D]) -> float:
        n1, n2 = nodes[self.start_node], nodes[self.end_node]
        return math.sqrt(
            (n2.x - n1.x) ** 2 + (n2.y - n1.y) ** 2 + (n2.z - n1.z) ** 2
        )


@dataclass
class FrameGeometry3D:
    nodes: Dict[int, Node3D]
    members: List[Member3D]
    connections: List[Connection]
    material: Dict[str, float] = field(
        default_factory=lambda: CHROMOLY_4130.copy()
    )

    def assembly_nodes(self, name: str) -> List[Node3D]:
        member_node_ids: Set[int] = set()
        for m in self.members:
            if m.assembly == name:
                member_node_ids.add(m.start_node)
                member_node_ids.add(m.end_node)
        return [self.nodes[nid] for nid in sorted(member_node_ids)]

    def assembly_members(self, name: str) -> List[Member3D]:
        return [m for m in self.members if m.assembly == name]

    def fixed_node_ids(self) -> List[int]:
        return [c.node_id for c in self.connections if c.bc_type == "fixed"]

    def load_node_id(self) -> int:
        for c in self.connections:
            if c.conn_type == "coupler_pin":
                return c.node_id
        raise ValueError("No coupler pin node found")


def build_gt1r_frame_3d(
    bar_od: float = 1.5,
    bar_wall: float = 0.120,
    strut_od: float = 1.5,
    strut_wall: float = 0.120,
    arm_length: float = 18.0,
) -> FrameGeometry3D:
    """
    Build full 3D geometry for both frame assemblies.

    Coordinate system (vehicle-centric):
        X = transverse (left-right, positive right)
        Y = longitudinal (forward positive)
        Z = vertical (up positive)
        Origin at left C3 mount (rear trunk frame).
    """
    bar_props = tube_section_properties(bar_od, bar_wall)
    strut_props = tube_section_properties(strut_od, strut_wall)

    # --- Assembly 1: Rear Trunk Frame (Page 1) ---
    nodes = {
        0: Node3D(0, 0.0, 0.0, 0.0, "left_c3_mount", "rear_trunk"),
        1: Node3D(1, 6.0, 0.0, 0.0, "left_bar_strut_jn", "rear_trunk"),
        2: Node3D(2, 18.0, 0.0, 0.0, "center_c1_bolt", "rear_trunk"),
        3: Node3D(3, 30.0, 0.0, 0.0, "right_bar_strut_jn", "rear_trunk"),
        4: Node3D(4, 36.0, 0.0, 0.0, "right_c3_mount", "rear_trunk"),
        5: Node3D(5, 18.0, 0.0, -7.25, "coupler_pin", "rear_trunk"),
        6: Node3D(6, 18.0, -arm_length, -7.25, "rear_bracket", "rear_trunk"),
    }

    members = [
        Member3D(0, 0, 1, "bar_left_end", "rear_trunk", bar_props),
        Member3D(1, 1, 2, "bar_left_center", "rear_trunk", bar_props),
        Member3D(2, 2, 3, "bar_center_right", "rear_trunk", bar_props),
        Member3D(3, 3, 4, "bar_right_end", "rear_trunk", bar_props),
        Member3D(4, 1, 5, "v_strut_left", "rear_trunk", strut_props),
        Member3D(5, 3, 5, "v_strut_right", "rear_trunk", strut_props),
        Member3D(6, 5, 6, "parachute_arm", "rear_trunk", strut_props),
    ]

    connections = [
        Connection(0, "C3", "fixed", "Weld — rigid BC at left frame rail"),
        Connection(1, "C0", "free", "Weld — bar to strut junction (left)"),
        Connection(2, "C1", "free", "Bolt + pin — center bar connection"),
        Connection(3, "C0", "free", "Weld — bar to strut junction (right)"),
        Connection(4, "C3", "fixed", "Weld — rigid BC at right frame rail"),
        Connection(5, "coupler_pin", "free", "Double pin — strut convergence"),
        Connection(6, "bracket", "free", "Rear bumper bracket — chute attach"),
    ]

    # --- Assembly 2: Under-Hood Frame (Page 2) ---
    # Positioned forward of trunk frame.
    # C3 mounts (N0, N4) connect to hood bar via frame rails.
    # Hood bar is offset forward (Y) and up (Z) relative to trunk origin.
    hood_y = 60.0   # ~5 ft forward of trunk bar (vehicle length estimate)
    hood_z = 12.0   # elevated relative to trunk bar

    nodes[7] = Node3D(
        7, 0.0, hood_y, hood_z, "hood_bar_left", "under_hood"
    )
    nodes[8] = Node3D(
        8, 14.0, hood_y, hood_z, "hood_bar_right", "under_hood"
    )
    nodes[9] = Node3D(
        9, 19.0, hood_y, hood_z - 1.0,
        "b1_bolted_connection", "under_hood",
    )
    nodes[10] = Node3D(
        10, 14.0, hood_y + 8.0, hood_z,
        "p1_pinned_bc", "under_hood",
    )

    members.extend([
        Member3D(7, 7, 8, "hood_bar_main", "under_hood", bar_props),
        Member3D(8, 8, 9, "hood_bar_end", "under_hood", bar_props),
        Member3D(9, 8, 10, "curved_arm", "under_hood", bar_props),
    ])

    # Frame rail links (connecting trunk to hood through vehicle chassis)
    members.extend([
        Member3D(10, 0, 7, "frame_rail_left", "frame_rail", bar_props),
        Member3D(11, 4, 8, "frame_rail_right", "frame_rail", bar_props),
    ])

    connections.extend([
        Connection(7, "C2", "free", "Weld — hood bar to chassis"),
        Connection(8, "C2", "free", "Weld — hood bar right end"),
        Connection(9, "B1", "bolted", "6x bolted connection to subframe"),
        Connection(10, "P1", "pinned", "Pinned boundary condition"),
    ])

    return FrameGeometry3D(
        nodes=nodes, members=members, connections=connections
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/test_frame_geometry_3d.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git add digitalmodel/src/digitalmodel/structural/parachute/frame_geometry_3d.py digitalmodel/tests/structural/parachute/test_frame_geometry_3d.py && git commit -m "feat(parachute): add 3D frame geometry data model — rear trunk + under-hood"'
```

---

## Task 2: Geometry Dimension Tests

**Files:**
- Modify: `tests/structural/parachute/test_frame_geometry_3d.py`

- [ ] **Step 1: Write failing dimension tests**

```python
# Add to test_frame_geometry_3d.py

class TestRearTrunkDimensions:
    """Verify rear trunk geometry matches hand sketch (Page 1)."""

    def setup_method(self):
        self.geo = build_gt1r_frame_3d()

    def test_total_bar_width_36in(self):
        n0, n4 = self.geo.nodes[0], self.geo.nodes[4]
        width = abs(n4.x - n0.x)
        assert abs(width - 36.0) < 0.01

    def test_segment_6_12_12_6(self):
        n = self.geo.nodes
        assert abs(n[1].x - n[0].x - 6.0) < 0.01
        assert abs(n[2].x - n[1].x - 12.0) < 0.01
        assert abs(n[3].x - n[2].x - 12.0) < 0.01
        assert abs(n[4].x - n[3].x - 6.0) < 0.01

    def test_coupler_pin_vertical_offset_7_25in(self):
        n2, n5 = self.geo.nodes[2], self.geo.nodes[5]
        assert abs(n2.z - n5.z - 7.25) < 0.01

    def test_coupler_pin_centered_at_x18(self):
        n5 = self.geo.nodes[5]
        assert abs(n5.x - 18.0) < 0.01

    def test_horizontal_bar_is_coplanar_z0(self):
        for nid in [0, 1, 2, 3, 4]:
            assert abs(self.geo.nodes[nid].z) < 0.01

    def test_v_strut_length(self):
        expected = math.sqrt(12.0**2 + 7.25**2)
        m4 = self.geo.members[4]  # v_strut_left
        actual = m4.length(self.geo.nodes)
        assert abs(actual - expected) < 0.01

    def test_v_struts_symmetric(self):
        m4 = self.geo.members[4]
        m5 = self.geo.members[5]
        l4 = m4.length(self.geo.nodes)
        l5 = m5.length(self.geo.nodes)
        assert abs(l4 - l5) < 0.01

    def test_parachute_arm_length(self):
        m6 = self.geo.members[6]
        length = m6.length(self.geo.nodes)
        assert abs(length - 18.0) < 0.01

    def test_frame_symmetric_about_x18(self):
        n = self.geo.nodes
        assert abs(n[0].x + n[4].x - 36.0) < 0.01
        assert abs(n[1].x + n[3].x - 36.0) < 0.01
        assert abs(n[0].z - n[4].z) < 0.01


class TestUnderHoodDimensions:
    """Verify under-hood geometry matches hand sketch (Page 2)."""

    def setup_method(self):
        self.geo = build_gt1r_frame_3d()

    def test_hood_bar_main_length_14in(self):
        m7 = [m for m in self.geo.members if m.label == "hood_bar_main"][0]
        length = m7.length(self.geo.nodes)
        assert abs(length - 14.0) < 0.01

    def test_hood_bar_end_approx_5in(self):
        m8 = [m for m in self.geo.members if m.label == "hood_bar_end"][0]
        length = m8.length(self.geo.nodes)
        expected = math.sqrt(5.0**2 + 1.0**2)
        assert abs(length - expected) < 0.1

    def test_b1_vertical_offset_1in(self):
        n8, n9 = self.geo.nodes[8], self.geo.nodes[9]
        assert abs(n8.z - n9.z - 1.0) < 0.01


class TestConnectionMetadata:
    def setup_method(self):
        self.geo = build_gt1r_frame_3d()

    def test_fixed_bc_nodes(self):
        fixed = self.geo.fixed_node_ids()
        assert 0 in fixed  # left C3
        assert 4 in fixed  # right C3

    def test_load_application_node(self):
        assert self.geo.load_node_id() == 5

    def test_b1_bolted_connection(self):
        b1 = [c for c in self.geo.connections if c.conn_type == "B1"]
        assert len(b1) == 1
        assert b1[0].bc_type == "bolted"

    def test_p1_pinned_connection(self):
        p1 = [c for c in self.geo.connections if c.conn_type == "P1"]
        assert len(p1) == 1
        assert p1[0].bc_type == "pinned"

    def test_all_connections_have_description(self):
        for c in self.geo.connections:
            assert len(c.description) > 0


class TestSectionProperties:
    def setup_method(self):
        self.geo = build_gt1r_frame_3d()

    def test_frame_rail_assembly_exists(self):
        rails = self.geo.assembly_members("frame_rail")
        assert len(rails) == 2  # left + right frame rail links

    def test_all_members_have_section_area(self):
        for m in self.geo.members:
            assert "A" in m.section
            assert m.section["A"] > 0

    def test_all_members_have_inertia(self):
        for m in self.geo.members:
            assert "I" in m.section

    def test_custom_tube_dimensions(self):
        geo = build_gt1r_frame_3d(bar_od=1.75, bar_wall=0.095)
        m0 = geo.members[0]
        assert abs(m0.section["OD"] - 1.75) < 0.01
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/test_frame_geometry_3d.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git add digitalmodel/tests/structural/parachute/test_frame_geometry_3d.py && git commit -m "test(parachute): add dimension + connection tests for 3D frame geometry"'
```

---

## Task 3: FreeCAD Frame Builder

**Files:**
- Create: `src/digitalmodel/structural/parachute/freecad_frame_builder.py`
- Create: `tests/structural/parachute/test_freecad_frame_builder.py`

- [ ] **Step 1: Write failing test (with FreeCAD skip guard)**

```python
# tests/structural/parachute/test_freecad_frame_builder.py
"""
Tests for FreeCAD frame builder — creates 3D tube model from geometry.
Requires FreeCAD — skipped if not available.
"""
import pytest

try:
    import FreeCAD
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not FREECAD_AVAILABLE, reason="FreeCAD not installed"
)

if FREECAD_AVAILABLE:
    from digitalmodel.structural.parachute.frame_geometry_3d import (
        build_gt1r_frame_3d,
    )
    from digitalmodel.structural.parachute.freecad_frame_builder import (
        build_freecad_model,
    )


class TestFreeCADModelCreation:
    def setup_method(self):
        self.geo = build_gt1r_frame_3d()
        self.doc = build_freecad_model(self.geo)

    def teardown_method(self):
        if self.doc:
            FreeCAD.closeDocument(self.doc.Name)

    def test_document_created(self):
        assert self.doc is not None
        assert self.doc.Name == "GT1R_ParachuteFrame"

    def test_tube_objects_created(self):
        tubes = [o for o in self.doc.Objects if "tube_" in o.Name.lower()]
        assert len(tubes) >= 6  # at least rear trunk members

    def test_tube_has_shape(self):
        tubes = [o for o in self.doc.Objects if "tube_" in o.Name.lower()]
        for t in tubes:
            assert hasattr(t, "Shape")
            assert t.Shape.Volume > 0

    def test_connection_markers_created(self):
        markers = [o for o in self.doc.Objects if "conn_" in o.Name.lower()]
        assert len(markers) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/test_freecad_frame_builder.py -v`
Expected: FAIL — ImportError (module doesn't exist) or SKIP (if FreeCAD not found)

- [ ] **Step 3: Write FreeCAD builder implementation**

```python
# src/digitalmodel/structural/parachute/freecad_frame_builder.py
"""
ABOUTME: FreeCAD model builder for GT1R parachute frame
ABOUTME: Creates 3D tube solids from frame_geometry_3d, exports STEP
"""
import math
import sys
import os
from pathlib import Path
from typing import Optional

# FreeCAD path setup
FREECAD_LIB_PATHS = [
    "/usr/lib/freecad-python3/lib",
    "/usr/lib/freecad/lib",
]
for p in FREECAD_LIB_PATHS:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

try:
    import FreeCAD  # noqa: E402
    import Part  # noqa: E402
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False

from digitalmodel.structural.parachute.frame_geometry_3d import (
    FrameGeometry3D,
    Member3D,
    Node3D,
)


def _require_freecad():
    if not FREECAD_AVAILABLE:
        raise RuntimeError(
            "FreeCAD not available — install FreeCAD or run via freecadcmd"
        )


def _make_tube(
    doc: FreeCAD.Document,
    name: str,
    start: Node3D,
    end: Node3D,
    od: float,
    wall: float,
) -> "Part.Feature":
    """Create a hollow tube (pipe) between two 3D points."""
    p1 = FreeCAD.Vector(start.x, start.y, start.z)
    p2 = FreeCAD.Vector(end.x, end.y, end.z)
    direction = p2 - p1
    length = direction.Length

    if length < 1e-6:
        raise ValueError(f"Zero-length member: {name}")

    # Use makeCylinder with base point + direction — handles all
    # orientations natively (no manual rotation needed)
    outer = Part.makeCylinder(od / 2, length, p1, direction)
    inner = Part.makeCylinder((od - 2 * wall) / 2, length, p1, direction)
    tube_shape = outer.cut(inner)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = tube_shape
    return obj


def _make_connection_marker(
    doc: FreeCAD.Document,
    name: str,
    node: Node3D,
    conn_type: str,
    radius: float = 0.5,
) -> "Part.Feature":
    """Place a small sphere at connection location as visual marker."""
    sphere = Part.makeSphere(radius, FreeCAD.Vector(node.x, node.y, node.z))
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = sphere
    return obj


def build_freecad_model(
    geo: FrameGeometry3D,
    doc_name: str = "GT1R_ParachuteFrame",
) -> FreeCAD.Document:
    """
    Build FreeCAD document with tube solids for all frame members.

    Returns the FreeCAD Document object.
    """
    _require_freecad()
    doc = FreeCAD.newDocument(doc_name)

    for member in geo.members:
        start = geo.nodes[member.start_node]
        end = geo.nodes[member.end_node]
        od = member.section.get("OD", 1.5)
        wall = member.section.get("wall", 0.120)
        name = f"Tube_{member.id}_{member.label}"
        _make_tube(doc, name, start, end, od, wall)

    for conn in geo.connections:
        node = geo.nodes[conn.node_id]
        name = f"Conn_{conn.node_id}_{conn.conn_type}"
        _make_connection_marker(doc, name, node, conn.conn_type)

    doc.recompute()
    return doc


def export_step(doc: FreeCAD.Document, output_path: str) -> str:
    """Export all objects to STEP file for meshing."""
    shapes = [o for o in doc.Objects if hasattr(o, "Shape")]
    if not shapes:
        raise ValueError("No shapes in document to export")
    Part.export(shapes, output_path)
    return output_path


def export_iges(doc: FreeCAD.Document, output_path: str) -> str:
    """Export all objects to IGES file."""
    shapes = [o for o in doc.Objects if hasattr(o, "Shape")]
    if not shapes:
        raise ValueError("No shapes in document to export")
    Part.export(shapes, output_path)
    return output_path
```

- [ ] **Step 4: Run tests**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/test_freecad_frame_builder.py -v`
Expected: PASS (if FreeCAD available on ace-linux-2) or SKIP (on ace-linux-1)

- [ ] **Step 5: Commit**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git add digitalmodel/src/digitalmodel/structural/parachute/freecad_frame_builder.py digitalmodel/tests/structural/parachute/test_freecad_frame_builder.py && git commit -m "feat(parachute): add FreeCAD frame builder — tubes + connection markers + STEP export"'
```

---

## Task 4: STEP Export Test

**Files:**
- Modify: `tests/structural/parachute/test_freecad_frame_builder.py`

- [ ] **Step 1: Write failing STEP export test**

```python
# Add to test_freecad_frame_builder.py
import tempfile
import os

from digitalmodel.structural.parachute.freecad_frame_builder import (
    export_step,
    export_iges,
)


class TestSTEPExport:
    def setup_method(self):
        self.geo = build_gt1r_frame_3d()
        self.doc = build_freecad_model(self.geo)

    def teardown_method(self):
        if self.doc:
            FreeCAD.closeDocument(self.doc.Name)

    def test_step_export_creates_file(self):
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
            path = f.name
        try:
            result = export_step(self.doc, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)

    def test_step_export_returns_path(self):
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
            path = f.name
        try:
            result = export_step(self.doc, path)
            assert result == path
        finally:
            os.unlink(path)

    def test_iges_export_creates_file(self):
        with tempfile.NamedTemporaryFile(suffix=".iges", delete=False) as f:
            path = f.name
        try:
            result = export_iges(self.doc, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)
```

- [ ] **Step 2: Run tests**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/test_freecad_frame_builder.py::TestSTEPExport -v`
Expected: PASS or SKIP

- [ ] **Step 3: Commit**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git add digitalmodel/tests/structural/parachute/test_freecad_frame_builder.py && git commit -m "test(parachute): add STEP export integration test"'
```

---

## Task 5: Update __init__.py + Run Full Test Suite

**Files:**
- Modify: `src/digitalmodel/structural/parachute/__init__.py`

- [ ] **Step 1: Update __init__.py**

```python
"""
ABOUTME: Parachute frame structural analysis package
ABOUTME: Drag force, frame geometry (2D/3D), solver, and member checks
"""
```

(Keep it minimal — no imports of FreeCAD-dependent modules at package level.)

- [ ] **Step 2: Run full parachute test suite**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/ -v`
Expected: All existing tests PASS + new geometry tests PASS + FreeCAD tests PASS/SKIP

- [ ] **Step 3: Commit**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git add digitalmodel/src/digitalmodel/structural/parachute/__init__.py && git commit -m "chore(parachute): update __init__.py docstring for 3D geometry module"'
```

---

## Task 6: CLI Script for Model Generation

**Files:**
- Create: `src/digitalmodel/structural/parachute/generate_frame_cad.py`

- [ ] **Step 1: Create CLI entry point**

```python
# src/digitalmodel/structural/parachute/generate_frame_cad.py
"""
ABOUTME: CLI script to generate FreeCAD model and STEP export
ABOUTME: Usage: freecadcmd generate_frame_cad.py [--output-dir DIR]
"""
import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Generate GT1R parachute frame FreeCAD model"
    )
    parser.add_argument(
        "--output-dir", default=".", help="Output directory for STEP/FCStd"
    )
    parser.add_argument(
        "--bar-od", type=float, default=1.5, help="Bar tube OD (inches)"
    )
    parser.add_argument(
        "--bar-wall", type=float, default=0.120, help="Bar wall thickness"
    )
    args = parser.parse_args()

    from digitalmodel.structural.parachute.frame_geometry_3d import (
        build_gt1r_frame_3d,
    )
    from digitalmodel.structural.parachute.freecad_frame_builder import (
        build_freecad_model,
        export_step,
    )
    import FreeCAD

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    geo = build_gt1r_frame_3d(bar_od=args.bar_od, bar_wall=args.bar_wall)
    doc = build_freecad_model(geo)

    step_path = str(out / "gt1r_parachute_frame.step")
    export_step(doc, step_path)
    print(f"STEP exported: {step_path}")

    fcstd_path = str(out / "gt1r_parachute_frame.FCStd")
    doc.saveAs(fcstd_path)
    print(f"FreeCAD file: {fcstd_path}")

    FreeCAD.closeDocument(doc.Name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Test CLI manually**

Run: `cd /mnt/workspace-hub/digitalmodel && PYTHONPATH=src freecadcmd src/digitalmodel/structural/parachute/generate_frame_cad.py --output-dir /tmp/gt1r-frame`
Expected: Files created at `/tmp/gt1r-frame/gt1r_parachute_frame.step` and `.FCStd`

- [ ] **Step 3: Commit**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git add digitalmodel/src/digitalmodel/structural/parachute/generate_frame_cad.py && git commit -m "feat(parachute): add CLI script for FreeCAD model + STEP generation"'
```

---

## Task 7: Push + Move WRK to Done

- [ ] **Step 1: Push all commits**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && git push'
```

- [ ] **Step 2: Move WRK-1360 to done**

```bash
ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && mv .claude/work-queue/pending/WRK-1360.md .claude/work-queue/done/WRK-1360.md'
```

- [ ] **Step 3: Update WRK-1360 status**

Set `status: done` in frontmatter.

---

## Acceptance Criteria Mapping

| AC | Task |
|---|---|
| FreeCAD model includes both assemblies (rear trunk + under-hood) | Task 1 (geometry), Task 3 (FreeCAD) |
| All 6 connection types represented with correct BC type | Task 1 (connections list), Task 2 (connection tests) |
| Member dimensions match hand sketch (±0.25") | Task 2 (dimension tests) |
| Tube cross-section properties extractable | Task 2 (section property tests) |
| Model exports to STEP/IGES | Task 4 (STEP export test) |
