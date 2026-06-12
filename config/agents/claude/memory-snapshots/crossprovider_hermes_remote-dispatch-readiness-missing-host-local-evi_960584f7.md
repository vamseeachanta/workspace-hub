---
name: crossprovider hermes remote-dispatch-readiness-missing-host-local-evi
description: Remote dispatch readiness missing host-local evidence enforcement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, readiness, correctness-blocker, multi-machine]
---

Dispatch policy accepts `status in {"pass", "warn"}` for remote hosts without requiring proof of local state. Caller can provide any HostReadiness dict without validation. Remote hosts must provide timestamped host-local evidence (git status, Hermes readiness timestamp) or dispatch must fail; status=warn alone is insufficient.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
