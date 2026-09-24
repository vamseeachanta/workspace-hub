---
name: crossprovider codex domain-and-local-account-principals-on-windows-a
description: Domain and local account principals on Windows are not interchangeable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [windows-auth, fleet-design, ssh-principals]
---

Two accounts may both SSH-auth to the same Windows host but reach completely different resource sets (e.g., one reaches file servers, the other cannot). Recording reachability without the principal (domain account vs local account) is architecturally incomplete and will fail at runtime. Scheduled tasks and stored credentials must be registered under the correct principal type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
