---
name: crossprovider codex freshness-needs-multiple-mechanisms-not-just-hoo
description: Freshness needs multiple mechanisms, not just hook-based
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [freshness, caching, hooks, state-management]
---

Post-merge hooks only fire on merges; they miss local edits, rebases, or checkouts from other roots. For systems with generated indices or cached state, add explicit freshness checks or warnings, not just best-effort hook rebuilds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
