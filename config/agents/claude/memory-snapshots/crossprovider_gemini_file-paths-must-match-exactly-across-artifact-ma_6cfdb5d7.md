---
name: crossprovider gemini file-paths-must-match-exactly-across-artifact-ma
description: File paths must match exactly across Artifact Map, Pseudocode, and Acceptance Criteria
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [plan-review, correctness, testing]
---

Mismatches between path definitions cause test failures and file-globbing self-ingestion (e.g., output pattern overlaps input pattern in re-runs). Trace paths through all plan sections; inconsistencies between where files are written and where tests read them are a common correctness trap.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
