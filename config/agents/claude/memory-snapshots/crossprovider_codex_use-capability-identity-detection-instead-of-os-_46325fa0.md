---
name: crossprovider codex use-capability-identity-detection-instead-of-os-
description: Use capability/identity detection instead of OS strings for security gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [platform-detection, security, implementation-hazard]
---

Gating security checks on `os == "linux"` creates exploitable bypasses: a dispatch-enabled macOS host can report pass without proving workspace exists, is a git repo, or has upstream. Use identity matching (socket.gethostname() vs registry host metadata) and capability probes instead of OS declarations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
