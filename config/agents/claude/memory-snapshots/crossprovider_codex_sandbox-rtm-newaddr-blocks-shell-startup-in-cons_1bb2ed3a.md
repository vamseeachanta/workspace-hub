---
name: crossprovider codex sandbox-rtm-newaddr-blocks-shell-startup-in-cons
description: Sandbox RTM_NEWADDR blocks shell startup in constrained bwrap environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sandbox-constraints, bwrap-blocking, operational-blocker, environment]
---

Shell invocation fails immediately with 'bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted' in certain sandboxed contexts, blocking all subsequent execution before any command runs. Defer execution to unconstrained hosts (e.g., dev-secondary with full permissions) rather than attempting workarounds requiring elevated permissions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
