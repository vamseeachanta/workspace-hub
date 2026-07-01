---
name: crossprovider codex phase-specific-public-scan-manifests-prevent-ove
description: Phase-specific public-scan manifests prevent overly broad targets
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [phasing, scope, scan-targets, plan-design]
---

When plans span multiple implementation phases, define phase-specific scan target sets rather than uniform manifests. Each phase validates only its actual scope. This prevents the front-loaded phase from forcing scan coverage for work defined in later phases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
