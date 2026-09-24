---
name: crossprovider codex license-verification-from-authoritative-files-no
description: License verification from authoritative files, not prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [license-verification, compliance, oss-ingest]
---

Always verify licenses from LICENSE/COPYING files and git metadata, not README prose. Different GPL versions (2.0 vs. 3.0 with or without "later", linking exceptions) are substantively different and must not be collapsed generically. Check multiple sources (LICENSE, git history, pyproject.toml, docs) and flag discrepancies in the ingested page rather than silently normalizing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
