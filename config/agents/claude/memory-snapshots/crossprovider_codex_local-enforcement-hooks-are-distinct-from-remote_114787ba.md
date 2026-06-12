---
name: crossprovider codex local-enforcement-hooks-are-distinct-from-remote
description: Local enforcement hooks are distinct from remote approval semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [enforcement, gates, decoupling, local-vs-remote]
---

.claude/hooks/plan-approval-gate.sh is authoritative only for local write-gate behavior and safe-path exemptions. GitHub approval semantics live in docs/plans/README.md and skill definitions. These can drift; don't conflate them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
