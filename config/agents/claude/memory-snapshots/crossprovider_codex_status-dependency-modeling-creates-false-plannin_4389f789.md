---
name: crossprovider codex status-dependency-modeling-creates-false-plannin
description: Status/dependency modeling creates false planning gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning-process, status-modeling, gate-accuracy]
---

Plans marked `status: draft` while internally claiming blocking dependencies (e.g., '#730 blocked by #729') allow downstream work to proceed on unmet prerequisites. Verify at review time: if a plan text says 'blocked by X', frontmatter must say `status: blocked` and README must reflect that, not draft.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
