---
name: crossprovider codex cleanup-audit-classification-depends-on-plan-ref
description: Cleanup audit classification depends on plan references and history
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup-pattern, artifact-lifecycle]
---

Classify dirty files as PRESERVE-COMMIT (durable plan references, findings), GENERATED-DISCARD-CANDIDATE (stale generated state replaced by UNAVAILABLE), or DEFER (unrelated scope). Always check git history and plan artifacts; don't assume all dirty files belong to current scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
