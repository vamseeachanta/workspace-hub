---
name: crossprovider codex os-conditional-fail-closed-checks-create-inconsi
description: OS-conditional fail-closed checks create inconsistent security gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, cross-platform, fail-closed]
---

Critical readiness checks (workspace exists, git synced, data access) conditioned on OS type create bypass paths for local non-Linux hosts. Use local-vs-remote detection (socket-based) instead; apply the same rigor to all local hosts regardless of OS.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
