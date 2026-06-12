---
name: crossprovider codex fail-closed-for-missing-optional-dependencies-in
description: Fail-closed for missing optional dependencies in scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, dependency-management, fallback-patterns]
---

When external tools/libs (bleach, rg, timeout) may be unavailable, fail closed (skip feature, render unavailable message, log warning) rather than attempt degraded-but-functional fallbacks. Regex-based HTML sanitization is never a safe substitute for proper sanitizers like bleach; removed bleach from uv deps and changed fallback from regex patterns to explicit 'Content unavailable' message.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
