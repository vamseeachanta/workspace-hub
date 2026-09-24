---
name: crossprovider codex multi-machine-dispatch-requires-explicit-fail-cl
description: Multi-machine dispatch requires explicit fail-closed gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dispatch, multi-machine, hermes, fail-closed]
---

Remote dispatch (Telegram, Hermes, other) must fail closed on dirty/unsynced repos, missing approval markers, unsafe gateway config, missing env tokens, host evidence gaps, missing data access, duplicate leases, and workflow-gate violations. This pattern applies to any multi-host control plane.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
