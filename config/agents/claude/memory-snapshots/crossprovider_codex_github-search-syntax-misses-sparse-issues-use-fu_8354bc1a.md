---
name: crossprovider codex github-search-syntax-misses-sparse-issues-use-fu
description: GitHub search-syntax misses sparse issues; use full JSON pull + local filters
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [github-api, issue-discovery, search-pattern]
---

Compound OR queries and multi-filter chains silently skip sparse results in GitHub search. Instead pull all open issues as JSON, filter locally by title/labels/body. Avoids query-syntax dead zones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
