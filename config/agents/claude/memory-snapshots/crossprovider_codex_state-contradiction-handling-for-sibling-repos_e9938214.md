---
name: crossprovider codex state-contradiction-handling-for-sibling-repos
description: State contradiction handling for sibling repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [repo-state, anomaly-handling, provenance, sibling-checkouts]
---

When prior issue comments report repos moved to sibling checkouts but live filesystem probes find them absent, treat as explicit anomaly. Preserve historical provenance, emit warnings, and classify under `historically_moved_not_currently_present`. Silent hiding risks data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
