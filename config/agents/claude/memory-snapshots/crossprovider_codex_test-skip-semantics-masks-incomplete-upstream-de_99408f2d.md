---
name: crossprovider codex test-skip-semantics-masks-incomplete-upstream-de
description: Test skip semantics masks incomplete upstream deliverables
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [test-design, skip-semantics, dependency-verification]
---

#610 allows tests to skip when required dependencies (symbols like `OrcaWaveAssetResolver`) are missing, but after upstream #500-#606 land, missing symbols mean broken integration. Skip tests should fail when dependencies are supposed to exist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
