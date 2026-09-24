---
name: crossprovider codex enforcement-checks-must-cover-both-hooked-and-di
description: Enforcement checks must cover both hooked and direct code paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-architecture, security-gate, coverage]
---

A check placed only in a hook (e.g., PreToolUse) fails for direct code execution (Bash writes, Python imports). Enforcement requires guards at both hook-level AND script-level/stage-transition points, or it remains fail-open for non-hooked paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
