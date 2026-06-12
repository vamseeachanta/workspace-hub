---
name: crossprovider gemini spec-migration-idempotent-apply-requires-careful
description: Spec migration: idempotent apply requires careful README handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, specs, file-handling]
---

When migrating specs from local trees to centralized repos, source README.md files are copied as content first, then the local README.md is replaced with a pointer template. Pre-flight collision detection is essential; fail-fast if target files exist. (WRK-188 migration plan, v1.10+)

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
