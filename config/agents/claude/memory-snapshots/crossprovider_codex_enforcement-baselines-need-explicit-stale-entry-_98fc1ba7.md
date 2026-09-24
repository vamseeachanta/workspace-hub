---
name: crossprovider codex enforcement-baselines-need-explicit-stale-entry-
description: Enforcement baselines need explicit stale-entry detection in CI
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-scripts, ci-gates, baseline-management]
---

Baselines tracking valid occurrences can bloat and hide removals without CI logic to detect entries no longer appearing in scans. The model-id-guard baseline needed CI to report stale entries, preventing silent blind spots where old patterns are gone but baseline entries persist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
