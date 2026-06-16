---
name: crossprovider codex plan-files-must-specify-fail-closed-handling-for
description: Plan files must specify fail-closed handling for ignored local state
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [plan-design, ignored-files, prerequisites, error-handling]
---

Machine-local ignored files (e.g., data/document-index/index.jsonl, .cache/uv) are prerequisites that implementations depend on but plans cannot assume exist. Plans must require implementations to fail closed with clear prerequisite errors, not silently skip.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
