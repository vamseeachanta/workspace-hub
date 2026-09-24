---
name: crossprovider codex reuse-existing-repo-enforcement-patterns-for-con
description: Reuse existing repo enforcement patterns for contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-design, testing, code-reuse]
---

Repos typically have established test patterns for doc staleness, drift detection, and reference validation (e.g., test_staleness_scanner.py, test_banned_stale_references.py). New contract or governance documents should follow the same test style and locations rather than inventing new enforcement frameworks, reducing maintenance burden.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
