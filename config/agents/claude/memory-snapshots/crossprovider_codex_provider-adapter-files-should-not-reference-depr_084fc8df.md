---
name: crossprovider codex provider-adapter-files-should-not-reference-depr
description: Provider adapter files should not reference deprecated workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [provider-adapters, canonicalization, deprecated-surfaces, maintenance]
---

Thin adapters (.codex/CODEX.md, .gemini/GEMINI.md, .hermes/) must point to canonical AGENTS.md and current workflow surfaces. Audit for stale references to deprecated work-queue-workflow.md, WRK-* gates, or old gate-pass skills.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
