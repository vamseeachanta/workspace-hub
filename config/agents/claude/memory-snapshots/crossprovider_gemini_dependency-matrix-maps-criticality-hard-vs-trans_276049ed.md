---
name: crossprovider gemini dependency-matrix-maps-criticality-hard-vs-trans
description: Dependency matrix maps criticality: hard vs transitive vs soft
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [planning, dependencies, critical-path]
---

Plans include explicit dependency matrices (Issue → State → Relationship → Behavior-if-unshipped). Hard dependencies block implementation; transitive dependencies propagate hard constraints; soft dependencies are scope-separated and non-blocking. Example: #2402 marked HARD (implementation waits); #2403 marked transitive-hard (via #2402); #2206 marked soft (no blocking). Clarity on critical path vs optional work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
