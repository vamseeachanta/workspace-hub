---
name: crossprovider codex vague-scope-boundaries-on-autorewrite-tools-are-
description: Vague scope boundaries on autorewrite tools are blockers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scope-definition, safety-boundary, autorewrite-tools]
---

Plans targeting config/policy files with phrases like 'whitelisted surfaces' or 'open question' on exact paths create scope-creep risk. For tools that mutate repo structure, enumerate the exact allowlist (concrete paths/globs) and explicit exclusion rules upfront. Defer uncertain surfaces to follow-up issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
