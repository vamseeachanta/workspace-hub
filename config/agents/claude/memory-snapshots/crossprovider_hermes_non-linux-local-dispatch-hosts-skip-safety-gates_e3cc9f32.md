---
name: crossprovider hermes non-linux-local-dispatch-hosts-skip-safety-gates
description: Non-Linux local dispatch hosts skip safety gates in readiness checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch-validation, multi-os-readiness, safety-gap]
---

Readiness validation for workspace existence, git sync state, and data-access checks run only under `if raw.get("os") == "linux"`, causing non-Linux dispatch-enabled local hosts to pass with `dispatchable=true` despite missing workspace/VCS/data evidence. Violates fail-closed intent for multi-machine dispatch. Affects macOS/Windows local dispatch hosts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
