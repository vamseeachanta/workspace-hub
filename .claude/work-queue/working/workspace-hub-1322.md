---
id: workspace-hub#1322
title: "3D interactive frame viewer (HTML/three.js)"
status: working
priority: medium
complexity: medium
created_at: "2026-03-22"
parent: WRK-5082
blocked_by: []
target_repos: [workspace-hub, digitalmodel]
computer: dev-primary
orchestrator: claude
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: engineering-calculations
subcategory: visualization
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1322
stage_evidence_ref: .claude/work-queue/assets/WRK-1392/evidence/stage-evidence.yaml
route: B
plan_reviewed: true
plan_approved: true
percent_complete: 100
---

## Mission

Generate a browser-based 3D interactive viewer from `FrameGeometry3D` so the frame can be inspected without FreeCAD installed.

## What

1. Create a Python script that reads `FrameGeometry3D` and outputs a self-contained HTML file with three.js
2. Render tubes as cylinders, bends as arc-extruded profiles, connection markers as colored spheres
3. Color-code by assembly (rear trunk = blue, under-chassis = orange)
4. Mark BCs: fixed (red squares), bolted (dark red triangles), origin (gold diamond)
5. Add node labels, dimension annotations, and orbit/zoom controls
6. Include a toggle panel to show/hide assemblies, node labels, and connection markers

## Why

Currently the frame can only be viewed via:
- Static matplotlib PNG (no rotation)
- FreeCAD (requires installation on ace-linux-2)
- GitHub markdown stick figures

An interactive HTML viewer enables:
- Client review without software installation
- Quick geometry verification during iterative refinement
- Embedding in engineering reports (WRK-1368)

## Acceptance Criteria

- [x] Single self-contained HTML file (no external dependencies)
- [x] All 15 nodes, 16 members rendered with correct geometry
- [x] Bend members shown as curves, not straight lines
- [x] Orbit, zoom, pan controls
- [x] Node labels toggleable
- [x] Assembly color coding matches matplotlib preview
- [x] File opens in any modern browser
