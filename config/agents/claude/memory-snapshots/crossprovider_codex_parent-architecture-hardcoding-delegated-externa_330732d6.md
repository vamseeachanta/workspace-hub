---
name: crossprovider codex parent-architecture-hardcoding-delegated-externa
description: Parent architecture hardcoding delegated external namespaces
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [architecture, scope-creep, plan-compliance, delegation]
---

Locking unverified external service credentials (Hugging Face org, cloud account, auth realm) in parent contract when the approved plan delegates ownership to child preflight creates unfixable scope overstep. Use template placeholders (`{hf_org}`) with explicit `authentication_required` gates; let child publish-preflight verify and bind final targets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
