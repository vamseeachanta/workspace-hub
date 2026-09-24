---
name: crossprovider codex unsafe-compatibility-fallbacks-in-multi-schema-p
description: Unsafe compatibility fallbacks in multi-schema pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [compatibility, fallback-safety, schema-evolution, correctness]
---

When generating outputs from rows that may have missing/malformed identity fields, never fallback to raw source identity (source label, filename, path). Fail-closed (raise an error), validate against a safe-root policy, or use opaque placeholders. Untested branches where legacy/malformed rows trigger unsafe fallbacks are correctness defects that can leak private data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
