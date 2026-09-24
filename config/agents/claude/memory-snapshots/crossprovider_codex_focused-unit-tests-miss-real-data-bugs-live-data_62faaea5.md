---
name: crossprovider codex focused-unit-tests-miss-real-data-bugs-live-data
description: Focused unit tests miss real data bugs; live data probes are mandatory
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, data-quality]
---

Focused/happy-path unit tests can pass while real data exposes silent failures (e.g., pipe-delimited caveat tokenization collapse, null propagation without caveats, href generation with divergent root paths). Behavior verification for ingestion/dossier code requires probes against live source data, not just unit test coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
