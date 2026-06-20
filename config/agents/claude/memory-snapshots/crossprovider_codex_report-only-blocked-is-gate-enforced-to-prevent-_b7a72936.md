---
name: crossprovider codex report-only-blocked-is-gate-enforced-to-prevent-
description: Report-only-blocked is gate-enforced to prevent accidental closure
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [issue-workflow, gate-enforcement, safety-pattern]
---

Gate code explicitly checks `report_only`, `passed=false`, and `closeout_state=report-only-blocked` to prevent closure of blocked issues. This is a safety pattern in the enforcement layer, not just a metadata label—returns `allowed=False` with explicit reason.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
