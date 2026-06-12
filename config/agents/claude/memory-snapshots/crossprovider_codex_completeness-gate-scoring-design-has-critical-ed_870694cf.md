---
name: crossprovider codex completeness-gate-scoring-design-has-critical-ed
description: Completeness-gate scoring design has critical edge-case and gaming gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scoring, edge-cases, design, gates]
---

Adversarial review of #2798 found ~20 MAJOR defects: undefined tie-breaking (2 reporters, 2 values), no evidence-linking proof, test-inflation gaming (low-value tests), stale snapshot handling (no SHA binding), manual tampering (no immutability), no integration test for actual `gh issue close` block, and weak enforcement (bypassable env var).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
