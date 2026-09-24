---
name: crossprovider codex live-session-config-apply-needs-active-process-d
description: Live-session config apply needs active-process detection and array merge semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration, live-systems, safety, idempotence]
---

Configuration systems that mutate live-session settings need active-process detection, reload semantics documentation, and explicit waiver flags. Array merge for hooks/deny lists must be deterministic with conflict detection and stable ordering—ad-hoc append/replace diverges on re-runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
