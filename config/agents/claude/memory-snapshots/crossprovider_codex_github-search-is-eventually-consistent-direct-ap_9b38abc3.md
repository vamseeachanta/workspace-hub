---
name: crossprovider codex github-search-is-eventually-consistent-direct-ap
description: GitHub search is eventually consistent; direct API enumeration required for audit completeness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github, audit, eventual-consistency]
---

When performing cross-repository duplicate audits or scope inventory via GitHub issues, search-based lookups lag behind live state and may omit recent issues. Direct REST API enumeration with pagination is required to establish authoritative ground truth. Codex discovered this when auditing workspace-hub for "Landman Project Desk" scope—search missed issues that direct enumeration revealed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
