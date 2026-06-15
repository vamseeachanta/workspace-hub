---
name: crossprovider codex public-artifact-generators-leak-unresolved-targe
description: Public-artifact generators leak unresolved targets via warnings despite schema saying drop without naming
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, public-artifact, generator-validation]
---

Issue #102 shows the public-graph generator filtering unresolved targets from edges but recording them in summary["warnings"] and reports. Schema says drop without emitting; summary still names them. Fix: explicit filtering of warnings dict and removal of all references to skipped targets from report/summary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
