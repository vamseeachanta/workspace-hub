---
name: crossprovider codex generator-and-builder-determinism-requirement
description: Generator and builder determinism requirement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [builders, coverage, verification]
---

Long-running generator checks with worker pools must have explicit coverage tracking and deterministic output. Silent page omission or timeout-based coverage gaps hide bugs. Choose: deterministic in-memory rendering, narrowly reasoned exclusions with tests, or bounded checks with explicit coverage accounting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
