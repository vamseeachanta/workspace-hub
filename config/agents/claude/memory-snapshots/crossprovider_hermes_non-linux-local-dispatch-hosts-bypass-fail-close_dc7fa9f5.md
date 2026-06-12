---
name: crossprovider hermes non-linux-local-dispatch-hosts-bypass-fail-close
description: Non-Linux local dispatch hosts bypass fail-closed checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch-safety, os-specific-logic]
---

Workspace/git/data-access readiness checks are gated on `if os == "linux"`. Local dispatch-enabled macOS/Windows hosts with missing workspace_root/git/data report pass/dispatchable, violating fail-closed requirements. Move checks outside OS-specific branch to apply to all local hosts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
