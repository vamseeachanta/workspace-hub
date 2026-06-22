---
name: crossprovider codex generated-completeness-evidence-marks-gate-ready
description: Generated completeness evidence marks gate-ready before implementation commits exist
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [generated-artifacts, governance, testing-gap, temporal-constraints]
---

Completeness generator scripts emit `gate-ready: true`, `100% PASS`, and all acceptance criteria `met: true` while work is uncommitted and reviews still in-progress. Tests pass by accepting this premature state. Generated artifacts must enforce temporal ordering: gate-ready only after implementation commit, code review, and privacy scan artifacts exist in tree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
