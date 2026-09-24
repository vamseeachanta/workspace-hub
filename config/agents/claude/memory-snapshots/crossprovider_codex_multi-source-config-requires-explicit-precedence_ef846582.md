---
name: crossprovider codex multi-source-config-requires-explicit-precedence
description: Multi-source config requires explicit precedence and deduplication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-management, system-design, precedence-rules]
---

When legacy and new formats both apply (machines list + roles), ambiguous precedence causes double-installs or wrong-host execution. Define explicit dedupe key and priority order with conflict-case tests. Document in prose and schema.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
