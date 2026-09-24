---
name: crossprovider codex pytest-plugins-with-fixed-startup-cost-should-co
description: Pytest plugins with fixed startup cost should conditionally initialize by execution mode
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, performance, testing, conditional-execution]
---

Use `session.config.getoption('collectonly')` to skip expensive initialization (database analysis, git metadata, NumPy imports) during collection-only runs while preserving capabilities in full test lanes. This removes fixed-cost tax from fast paths without reducing coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
