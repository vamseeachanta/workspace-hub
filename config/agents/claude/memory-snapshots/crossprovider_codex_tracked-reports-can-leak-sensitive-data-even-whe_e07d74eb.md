---
name: crossprovider codex tracked-reports-can-leak-sensitive-data-even-whe
description: Tracked reports can leak sensitive data even when crawling is bounded
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [data-leakage, reports, redaction, git-safety]
---

Generated HTML/JSON reports that record raw private root paths, client identifiers, or quarantine directory names in committed artifacts expose sensitive information via git history, regardless of whether child traversal is blocked. Redaction to stable opaque IDs (e.g., `quarantine_001`) must happen at generation time, and tests must assert that raw private names and substrings do NOT appear in tracked artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
