---
name: crossprovider gemini repo-orchestration-via-associative-array-with-ea
description: Repo orchestration via associative array with early validation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, multi-repo, orchestration, pattern]
---

Multi-repo scripts benefit from a bash associative array mapping normalized repo names to paths. Validate repo existence and normalize names early, then route all downstream operations through the map. Include graceful fallbacks (e.g., 'repo not found') rather than failing silently.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
