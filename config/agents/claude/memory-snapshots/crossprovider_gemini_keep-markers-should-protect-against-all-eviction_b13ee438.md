---
name: crossprovider gemini keep-markers-should-protect-against-all-eviction
description: Keep markers should protect against all eviction rules or none
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [user-expectations, data-retention]
---

Users expect explicit `# keep` markers to prevent ALL data loss, not a subset of rules. WRK-637 memory compaction applied `# keep` only to rules 4–5 (dedup, trim) but not 1–2 (done-WRK, stale paths). This inconsistency is confusing and violates user intent. Either keep protects all, or document the exception clearly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
