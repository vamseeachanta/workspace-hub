---
name: crossprovider gemini docs-regression-tests-require-fixed-classificati
description: Docs regression tests require fixed classification buckets, not runtime judgment
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, docs-governance, regression-tests]
---

Explicitly partition docs into protected current instructional surfaces, intentional legacy redirect surfaces, and historical/fixture surfaces using fixed enums by path. Fixed buckets prevent flaky tests that accidentally allow stale references in non-current files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
