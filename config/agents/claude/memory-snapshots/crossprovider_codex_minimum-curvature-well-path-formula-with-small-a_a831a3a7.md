---
name: crossprovider codex minimum-curvature-well-path-formula-with-small-a
description: Minimum-curvature well-path formula with small-angle limit
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [survey-math, well-path]
---

Well-path TVD uses ratio factor `RF = 2/DL * tan(DL/2)` where DL is dogleg angle; apply small-angle limit `RF = 1.0` when `|DL| ≤ 1e-12` to avoid numerical instability. Reference: digitalmodel `workflow.py`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
