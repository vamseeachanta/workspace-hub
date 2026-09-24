---
name: crossprovider codex explicit-read-only-scope-bounding-for-derived-vi
description: Explicit read-only scope bounding for derived-view plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-design, scope-bounding, governance]
---

Plans that produce derived views or reports (e.g., continuous-planning-pipeline) should explicitly declare themselves read-only: reading and reporting evidence without mutating GitHub labels, approval markers, or issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
