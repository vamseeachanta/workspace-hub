---
name: crossprovider hermes svg-vector-geometry-needs-explicit-coordinate-va
description: SVG/vector geometry needs explicit coordinate validation tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [svg-geometry, visual-testing, unit-tests]
---

Subtle bugs in coordinate transforms (e.g., hardcoded offsets in rotation calculations) are invisible to code review. B1528: schematic force line rotated with `setSvgRotation(..., -angle + 50)` causing vector to point 11° off-axis. Render-critical geometry requires unit tests asserting expected vs actual endpoints.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
