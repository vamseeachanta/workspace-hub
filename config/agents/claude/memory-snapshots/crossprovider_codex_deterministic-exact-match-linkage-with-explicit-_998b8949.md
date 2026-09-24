---
name: crossprovider codex deterministic-exact-match-linkage-with-explicit-
description: Deterministic exact-match linkage with explicit collision handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integration, linking, determinism]
---

For linking/joining datasets (e.g., disclosure to sanctioned records), use canonical exact-match rules on key fields (operator, project_name) rather than fuzzy matching. Surface ambiguous collisions with explicit `AMBIGUOUS` status rather than guessing, avoiding silent data corruption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
