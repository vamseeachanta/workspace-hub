---
name: crossprovider codex migration-residue-workflow-as-privacy-safe-templ
description: Migration-residue workflow as privacy-safe template
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-template, privacy-patterns, reusable-precedent]
---

Issue #732 established reusable patterns: metadata-only filesystem walks (no body reads), timestamp redaction in output, delete-gate set false, output projection guards, and multi-stage adversarial review catching data-leakage escaping TDD. New archive/comparison workflows (#730/#734) should reuse this template rather than re-implementing privacy boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
