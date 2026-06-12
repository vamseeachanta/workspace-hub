---
name: crossprovider codex pre-commit-tool-configuration-divergence-creates
description: Pre-commit tool-configuration divergence creates silent blockers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pre-commit, baseline-gating, static-analysis, coordination]
---

If pre-commit runs a security/quality tool without baseline suppression while full-suite applies baselines, developers get false failures on untouched code. Pre-commit must either apply the same baselines as full-suite or have explicitly documented stricter behavior; silent divergence causes false blockers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
