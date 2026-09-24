---
name: crossprovider codex live-environment-probes-must-be-captured-as-time
description: Live environment probes must be captured as timestamped test fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-fixtures, environment-probes, evidence-capture]
---

SSH probe findings (missing CLIs, repo paths, mounted storage) must be captured with exact hostname, timestamp, and local discoveries as test fixtures, not hardcoded into implementation or test assumptions. Tests must assert the readiness integration consumes actual live evidence, not stale or fixture-only state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
