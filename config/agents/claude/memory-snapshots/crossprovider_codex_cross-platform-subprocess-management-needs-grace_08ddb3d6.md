---
name: crossprovider codex cross-platform-subprocess-management-needs-grace
description: Cross-platform subprocess management needs graceful gnu tool fallbacks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subprocess, cross-platform, shell-scripting]
---

macOS lacks GNU coreutils (timeout, setsid); submit-to-*.sh scripts need perl-based timeout alternatives or degraded-mode operation (run without setsid isolation). Hardcoding gnu tools freezes orchestrators on non-Linux.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
