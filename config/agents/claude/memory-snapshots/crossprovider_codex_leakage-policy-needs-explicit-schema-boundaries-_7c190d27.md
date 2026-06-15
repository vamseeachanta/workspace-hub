---
name: crossprovider codex leakage-policy-needs-explicit-schema-boundaries-
description: Leakage policy needs explicit schema boundaries to resolve conflicts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [governance, leakage, schema-design]
---

Repo-visible artifacts must define allowlist/schema distinguishing private path-rich manifests from public-facing pages. Check repo precedent for policy conflicts (e.g., existing wiki pages may intentionally include `/mnt/ace` paths). Ambiguities must be resolved before implementation, not discovered later.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
