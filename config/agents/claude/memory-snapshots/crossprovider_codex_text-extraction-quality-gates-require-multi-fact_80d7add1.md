---
name: crossprovider codex text-extraction-quality-gates-require-multi-fact
description: Text extraction quality gates require multi-factor analysis, not presence checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [text-extraction, quality-gates, testing]
---

Extraction quality gates fail-closed only when checking multiple factors: section presence, control-character count, and text density. Presence-only gates (checking for 'ABSTRACT' token) allow garbled/corrupted text to pass as full-fidelity. Regression tests must cover both missing sections AND corrupted/garbled data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
