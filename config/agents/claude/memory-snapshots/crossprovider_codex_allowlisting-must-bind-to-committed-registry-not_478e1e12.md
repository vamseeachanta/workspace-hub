---
name: crossprovider codex allowlisting-must-bind-to-committed-registry-not
description: Allowlisting must bind to committed registry, not filesystem shape
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, api-design, access-control]
---

Shape-based allowlisting (regex patterns accepting any path matching a form) leaks untracked/draft files as safe. Public-safety or access-control filters must check against a committed allowlist of specific files, rejecting anything not explicitly registered.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
