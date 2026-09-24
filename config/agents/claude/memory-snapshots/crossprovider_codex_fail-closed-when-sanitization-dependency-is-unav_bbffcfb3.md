---
name: crossprovider codex fail-closed-when-sanitization-dependency-is-unav
description: Fail-closed when sanitization dependency is unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, dependency-handling, fail-closed]
---

When an optional security dependency (e.g., `bleach`) import fails, return a safe placeholder or escaped content rather than attempting unsafe fallback. Never silently render unsanitized HTML.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
