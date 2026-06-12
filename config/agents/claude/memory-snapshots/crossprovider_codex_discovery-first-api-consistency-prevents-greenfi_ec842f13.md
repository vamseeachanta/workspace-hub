---
name: crossprovider codex discovery-first-api-consistency-prevents-greenfi
description: Discovery-first API consistency prevents greenfield rework in modular systems
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [code-review, patterns, api-consistency, modular-systems]
---

WRK-157 fatigue report implementation inspected existing modules (worked_examples.py, sn_comparison_report.py) before writing to mirror APIs, data flows, and patterns. In modular codebases, reading 3-5 similar modules before writing new ones prevents divergence and eliminates later refactoring to align with established conventions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
